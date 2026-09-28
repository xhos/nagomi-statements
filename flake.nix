{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.git-hooks.url = "github:cachix/git-hooks.nix";
  inputs.git-hooks.inputs.nixpkgs.follows = "nixpkgs";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    git-hooks,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python3;
      deps = ps:
        with ps; [
          pymupdf
          beautifulsoup4
          grpcio
          protobuf
          googleapis-common-protos
        ];
      devPython = python.withPackages (ps: deps ps ++ [ps.pytest ps.watchfiles]);
    in {
      formatter = pkgs.alejandra;

      checks.pre-commit = git-hooks.lib.${system}.run {
        src = ./.;
        hooks = {
          alejandra.enable = true;
          ruff.enable = true;
          ruff-format.enable = true;

          nix-build = {
            enable = true;
            name = "nix-build";
            entry = pkgs.lib.getExe (pkgs.writeShellApplication {
              name = "nix-build-check";
              runtimeInputs = [pkgs.nix];
              text = "nix build --no-link";
            });
            stages = ["pre-push"];
            pass_filenames = false;
            files = "\\.py$|pyproject\\.toml|flake\\.nix";
          };
        };
      };

      packages.default = python.pkgs.buildPythonApplication {
        pname = "nagomi-statements";
        version = self.shortRev or self.dirtyShortRev or "dev";
        src = ./.;
        pyproject = true;
        build-system = [python.pkgs.setuptools];
        dependencies = deps python.pkgs;
        nativeCheckInputs = [python.pkgs.pytestCheckHook];
        meta.mainProgram = "nagomi-statements";
      };

      devShells.default = pkgs.mkShell {
        shellHook = self.checks.${system}.pre-commit.shellHook;
        env.PYTHONPATH = "src";
        packages = with pkgs; [
          devPython
          buf
          grpc # grpc_python_plugin
          protobuf # protoc, for the builtin python plugins
          ruff

          (writeShellScriptBin "regen" ''
            rm -rf src/nagomi
            ${buf}/bin/buf generate
          '')

          (writeShellScriptBin "run" ''
            # absolute interpreter: watchfiles' wrapper changes PATH for the child,
            # so a bare `python` would resolve to one without the dependencies
            exec ${devPython}/bin/watchfiles --filter python "${devPython}/bin/python -m nagomi_statements.server" src
          '')

          (writeShellScriptBin "fmt" ''
            ${ruff}/bin/ruff check --fix . && ${ruff}/bin/ruff format .
          '')

          (writeShellScriptBin "bump-protos" ''
            git -C proto fetch origin
            git -C proto checkout main
            git -C proto pull --ff-only
            git add proto
            git commit -m "chore: bump proto files"
            git push
          '')
        ];
      };
    });
}
