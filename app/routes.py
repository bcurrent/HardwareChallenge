from flask import jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import text
from app import app, db, limiter, logger
from app.schemas import validate_submission
from app.scoring import GPUScorer
from app.models import Submission
from app.redis_client import update_leaderboard, get_top_submissions
from sqlalchemy import exc

scorer = GPUScorer()

@app.route('/')
def health_check():
    """Simple health check endpoint"""
    try:
        # Test database connection with proper text() wrapper
        db.session.execute(text('SELECT 1'))
        # Test Redis connection by getting leaderboard
        get_top_submissions(1)
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "redis": "connected"
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500

def allocate_slot(submission):
    """Allocate GPU slot to the given submission with proper locking"""
    try:
        # Use serializable isolation level for the entire operation
        with db.session.begin():
            # Clear any expired slots first
            expired = Submission.query.filter_by(slot_allocated=True).filter(
                Submission.timestamp <= datetime.utcnow() - timedelta(hours=24)
            ).with_for_update().all()

            for exp in expired:
                exp.slot_allocated = False

            # Check if there's any active slot with row-level locking
            active_slot = Submission.query.filter_by(slot_allocated=True).filter(
                Submission.timestamp > datetime.utcnow() - timedelta(hours=24)
            ).with_for_update().first()

            if not active_slot:
                submission.slot_allocated = True
                db.session.commit()
                logger.info(f"Allocated slot to submission {submission.id}")
                return True

            return False

    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in slot allocation: {str(e)}")
        db.session.rollback()
        return False
    except Exception as e:
        logger.error(f"Error allocating slot: {str(e)}")
        db.session.rollback()
        return False

@app.route('/submit_qualification', methods=['POST'])
@limiter.limit("10 per hour")  # Changed to use "per" instead of "/" for consistency
def submit_qualification():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate submission data
        validation_error = validate_submission(data)
        if validation_error:
            return jsonify({'error': 'Invalid submission format', 'details': validation_error}), 400

        # Calculate score within a try block
        try:
            score = scorer.calculate_score(data)
        except ValueError as e:
            return jsonify({'error': 'Score calculation failed', 'details': str(e)}), 400

        # Create submission within a transaction
        submission = Submission(
            metrics=data,
            score=score,
            timestamp=datetime.utcnow()
        )

        try:
            db.session.add(submission)
            db.session.flush()  # Get the ID without committing

            # Update Redis leaderboard
            if not update_leaderboard(submission.id, score):
                logger.error(f"Failed to update leaderboard for submission {submission.id}")

            db.session.commit()

            # Try to allocate slot if score is high enough
            top_submissions = get_top_submissions(1)
            if top_submissions and top_submissions[0][0] == submission.id:
                allocate_slot(submission)

            logger.info(f"New submission processed successfully with score {score}")
            return jsonify({
                'success': True,
                'score': score,
                'submission_id': submission.id
            }), 200

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error processing submission: {str(e)}")
            return jsonify({'error': 'Database error occurred'}), 500

    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        # Get top 10 submissions from Redis with error handling
        top_submissions_redis = get_top_submissions(10)
        if top_submissions_redis is None:
            return jsonify({'error': 'Failed to fetch leaderboard data'}), 500

        # Get submission details from database
        submissions_details = []
        for sub_id, score in top_submissions_redis:
            try:
                submission = Submission.query.get(sub_id)
                if submission:
                    submissions_details.append({
                        'submission_id': submission.id,
                        'score': submission.score,
                        'timestamp': submission.timestamp.isoformat()
                    })
            except exc.SQLAlchemyError as e:
                logger.error(f"Error fetching submission {sub_id}: {str(e)}")
                continue

        # Get current active slot with proper error handling
        try:
            current_slot = Submission.query.filter_by(
                slot_allocated=True
            ).filter(
                Submission.timestamp > datetime.utcnow() - timedelta(hours=24)
            ).first()

            # Allocate slot to top submission if no active slot
            if not current_slot and submissions_details:
                top_submission = Submission.query.get(submissions_details[0]['submission_id'])
                if top_submission:
                    allocate_slot(top_submission)
                    current_slot = top_submission

            return jsonify({
                'leaderboard': submissions_details,
                'current_slot': {
                    'submission_id': current_slot.id,
                    'expires_at': (current_slot.timestamp + timedelta(hours=24)).isoformat()
                } if current_slot else None
            }), 200

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error in slot management: {str(e)}")
            return jsonify({'error': 'Database error occurred'}), 500

    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500