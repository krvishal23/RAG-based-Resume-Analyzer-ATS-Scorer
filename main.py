"""Launch the Streamlit application when this file is run directly."""

import sys

from streamlit.web import cli as streamlit_cli


if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app.py", *sys.argv[1:]]
    raise SystemExit(streamlit_cli.main())