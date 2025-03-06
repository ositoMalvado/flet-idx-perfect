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
    MAIN_FILE = "main.py";  # Asegúrate de que esto coincida con la ubicación correcta
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
          uv pip install --upgrade pip  # Actualizar pip usando uv
          uv pip install "flet[all]" --upgrade
          uv pip install uv  # Instalar uv en el entorno virtual
          
          # Verificar si el proyecto ya está inicializado
          if [ ! -f pyproject.toml ]; then
            uv init
            uv run flet create app
            # Mover archivos de la carpeta app a la raíz, asegurándose de que la carpeta de destino esté vacía
            if [ -d app ]; then
              rm -rf src  # Eliminar la carpeta src si existe
              mv -f app/* .
              rm -rf app
              rm -f .gitattributes .python-version main.py README.md uv.lock
            fi
          fi
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
          uv pip install --upgrade pip  # Actualizar pip usando uv
          uv pip install "flet[all]" --upgrade
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