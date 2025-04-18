{ pkgs, ... }: {
  channel = "stable-23.11";
  packages = with pkgs; [
    python3
    jdk20
    networkmanager
    wirelesstools
    zrok
    aria2
  ];
  env = {
    VENV_DIR = ".venv";
    MAIN_FILE = "examples/flet_extension_example/src/main.py";
  };
  idx = {
    extensions = [
      "ms-python.python"
      "ms-python.debugpy"
      "charliermarsh.ruff"
    ];
    workspace = {
      onCreate = {
        create-venv = ''
          if [ ! -d "$VENV_DIR" ]; then
            python -m venv $VENV_DIR
            source $VENV_DIR/bin/activate
            pip install uv
            pip install --upgrade pip
            if [ ! -f pyproject.toml ]; then
              uv init
              uv add "flet[all]" --upgrade
              uv run flet create --template extension --project-name flet-extension
              rm -f .gitattributes .python-version main.py README.md uv.lock
            fi
          fi
        '';
        default.openFiles = [ "pyproject.toml" "$MAIN_FILE" ];
      };
      onStart = {
        activate-venv = ''
          if [ ! -d "$VENV_DIR" ]; then
            python -m venv $VENV_DIR
            source $VENV_DIR/bin/activate
            pip install --upgrade pip
            pip install uv
            uv pip install "flet[all]" --upgrade
          else
            source $VENV_DIR/bin/activate
          fi
        '';
        default.openFiles = [ "$MAIN_FILE" ];
      };
    };
    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "bash"
            "-c"
            "source $VENV_DIR/bin/activate && flet run $MAIN_FILE --web --port $PORT -d -r"
          ];
          env = { PORT = "$PORT"; };
          manager = "web";
        };
      };
    };
  };
}
