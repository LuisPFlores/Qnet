"""
QNet Agent – Flask Application
Quantum Network Intelligence Consolidator

Run with:  python app.py
"""

import logging
import json
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

import config
from database.db import init_db, get_session, get_engine
from database.models import Source, University, Company
from agent.core import QNetAgent
from agent.topic_engine import TopicEngine

# ── Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Flask app ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# ── Database init ──────────────────────────────────────────────────────
engine = get_engine()
init_db(engine)

# ── Store last fetch result in memory for display ──────────────────────
_last_fetch_result = {}


# ═══════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════


@app.route("/")
def dashboard():
    """Main dashboard with overview stats."""
    session = get_session(engine)
    try:
        agent = QNetAgent(session)
        stats = agent.get_dashboard_stats()
        return render_template("dashboard.html", stats=stats)
    finally:
        session.close()


@app.route("/articles")
def articles():
    """Articles listing with search and filters."""
    session = get_session(engine)
    try:
        agent = QNetAgent(session)

        search = request.args.get("search", "").strip()
        source_type = request.args.get("source_type", "").strip()
        content_type = request.args.get("content_type", "").strip()
        page = int(request.args.get("page", 1))
        per_page = 50
        offset = (page - 1) * per_page

        article_list = agent.get_all_articles(
            source_type=source_type or None,
            content_type=content_type or None,
            search=search or None,
            limit=per_page,
            offset=offset,
        )

        return render_template(
            "articles.html",
            articles=article_list,
            search=search,
            source_type=source_type,
            content_type=content_type,
            page=page,
        )
    finally:
        session.close()


@app.route("/hot-topics")
def hot_topics():
    """Hot topics ranking page."""
    session = get_session(engine)
    try:
        topic_engine = TopicEngine(session)
        topics = topic_engine.get_hot_topics(limit=30)
        trends = topic_engine.get_topic_trends()
        snapshot = topic_engine.get_latest_snapshot()
        analysis = snapshot.get("analysis", "")

        return render_template(
            "hot_topics.html",
            topics=topics,
            trends=trends,
            analysis=analysis,
        )
    finally:
        session.close()


@app.route("/universities")
def universities():
    """University research groups page."""
    session = get_session(engine)
    try:
        uni_list = session.query(University).order_by(University.country).all()
        return render_template("universities.html", universities=uni_list)
    finally:
        session.close()


@app.route("/sources")
def sources():
    """Data sources management page."""
    session = get_session(engine)
    try:
        source_list = (
            session.query(Source).order_by(Source.source_type, Source.name).all()
        )
        return render_template("sources.html", sources=source_list)
    finally:
        session.close()


@app.route("/latest")
def latest():
    """Show results of the last content fetch."""
    global _last_fetch_result
    return render_template("latest.html", result=_last_fetch_result or None)


# ═══════════════════════════════════════════════════════════════════════
#  API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════


@app.route("/api/fetch-latest", methods=["POST"])
def api_fetch_latest():
    """
    'Give me the last content' – triggers a full collection across all sources,
    runs AI analysis, updates hot topics, and returns a comprehensive summary.
    """
    global _last_fetch_result

    session = get_session(engine)
    try:
        agent = QNetAgent(session)
        logger.info("=== FETCH LATEST: Starting full collection ===")

        result = agent.collect_all()
        session.commit()

        _last_fetch_result = result
        logger.info(
            f"=== FETCH LATEST: Complete. {result['new_articles']} new articles. ==="
        )

        return jsonify({"success": True, "result": {
            "total_collected": result["total_collected"],
            "new_articles": result["new_articles"],
            "source_counts": result["source_counts"],
        }})

    except Exception as e:
        session.rollback()
        logger.error(f"Fetch latest failed: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        session.close()


@app.route("/api/stats")
def api_stats():
    """Get dashboard statistics as JSON."""
    session = get_session(engine)
    try:
        agent = QNetAgent(session)
        stats = agent.get_dashboard_stats()
        # Convert datetime objects for JSON serialization
        if stats["latest_snapshot"].get("generated_at"):
            stats["latest_snapshot"]["generated_at"] = str(
                stats["latest_snapshot"]["generated_at"]
            )
        return jsonify(stats)
    finally:
        session.close()


@app.route("/api/articles")
def api_articles():
    """Get articles as JSON with optional filters."""
    session = get_session(engine)
    try:
        agent = QNetAgent(session)
        search = request.args.get("search", "").strip()
        source_type = request.args.get("source_type", "").strip()
        content_type = request.args.get("content_type", "").strip()
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        article_list = agent.get_all_articles(
            source_type=source_type or None,
            content_type=content_type or None,
            search=search or None,
            limit=limit,
            offset=offset,
        )
        return jsonify(article_list)
    finally:
        session.close()


@app.route("/api/hot-topics")
def api_hot_topics():
    """Get hot topics as JSON."""
    session = get_session(engine)
    try:
        topic_engine = TopicEngine(session)
        topics = topic_engine.get_hot_topics(limit=30)
        return jsonify(topics)
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("Starting QNet Agent...")
    logger.info(f"Database: {config.DB_PATH}")
    logger.info(f"OpenAI model: {config.OPENAI_MODEL}")
    logger.info(
        f"OpenAI API key configured: {'Yes' if config.OPENAI_API_KEY else 'No'}"
    )
    app.run(debug=config.DEBUG, host="0.0.0.0", port=5000)
