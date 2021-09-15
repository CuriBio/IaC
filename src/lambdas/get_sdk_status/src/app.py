import logging
import sys


# remove AWS pre-config that interferes with custom config
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
# setup up custom basic config
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO, stream=sys.stdout
)
logger = logging.getLogger(__name__)
