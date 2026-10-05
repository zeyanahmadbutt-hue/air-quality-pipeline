import logging
import sys
from pathlib import Path
import psycopg
from extract import extract_all, CITIES
from transform import transform
from load import get_conn, init_schema, upsert
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
log = logging.getLogger("pipeline")
def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
def main():
    setup_logging()
    log.info("pipeline started")
    raw = extract_all()
    failed = sorted(set(CITIES) - {r["city"] for r in raw})
    if not raw:
        log.error("no cities extracted, aborting")
        return 1
    clean, stats = transform(raw)
    log.info("transform stats: %s", stats)
    if clean.empty:
        log.error("no valid rows after transform, aborting")
        return 1
    try:
        with get_conn() as conn:
            init_schema(conn)
            n = upsert(conn, clean)
    except psycopg.Error:
        log.exception("load failed")
        return 1
    log.info("upserted %d rows", n)
    if failed:
        log.warning("partial run, failed cities: %s", failed)
        return 2
    log.info("pipeline finished OK")
    return 0
if __name__ == "__main__":
    sys.exit(main())
