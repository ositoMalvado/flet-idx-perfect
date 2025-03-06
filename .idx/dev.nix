{ pkgs, ... }: {
  channel = "stable-23.11";

  packages = [
    pkgs.python3
    pkgs.jdk20
    pkgs.networkmanager
    pkgs.wirelesstools
    pkgs.zrok
    pkgs.aria2
  ];

  env = {
    VENV_DIR = ".venv";
    MAIN_FILE = "main.py";  # Actualizado para reflejar la ubicación correcta
  };

  idx = {
    extensions = [
      "ms-python.python"
      "ms-python.debugpy"
    ];

    workspace = {
      onCreate = {
        create-venv = ''
          python -m venv $VENV_DIR
          source $VENV_DIR/bin/activate
          pip install "flet[all]" --upgrade
          pip install uv
          uv init
          uv run flet create app
          mv -f app/* .
          rm -rf app
        '';
        default.openFiles = [ "pyproject.toml" "$MAIN_FILE" ];
      };

      onStart = {
        check-venv-existence = ''
          if [ ! -d $VENV_DIR ]; then
            echo "Creando entorno virtual..."
            python -m venv $VENV_DIR
          fi
          source $VENV_DIR/bin/activate
          pip install "flet[all]" --upgrade
        '';
        default.openFiles = [ "README.md" "requirements.txt" "$MAIN_FILE" ];
      };
    };

    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "bash"
            "-c"
            ''
            source $VENV_DIR/bin/activate
            flet run $MAIN_FILE --web --port $PORT -d -r
            ''
          ];
          env = { PORT = "$PORT"; };
          manager = "web";
        };
      };
    };
  };
}