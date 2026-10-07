export {};

type AetherSafeCommand =
  | "check_python"
  | "install_backend"
  | "run_backend_tests"
  | "install_frontend"
  | "typecheck"
  | "build";

interface AetherAPI {
  getAppInfo(): Promise<{
    name: string;
    version: string;
    platform: string;
  }>;

  getShellInfo(): Promise<{
    shell: string;
    platform: string;
  }>;

  runSafeCommand(command: AetherSafeCommand): Promise<{
    code: number;
    stdout: string;
    stderr: string;
  }>;
}

declare global {
  interface Window {
    aether: AetherAPI;
  }
}
