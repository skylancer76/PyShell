import os
import shutil
import subprocess
import shlex
import psutil
import time
import platform
import socket
from pathlib import Path
from commands_list import COMMANDS, COMMAND_HELP

class CommandProcessor:
    def __init__(self):
        # Set terminal root directory
        # Check for Vercel environment (/var/task) or local development
        if os.path.exists("/var/task"):
            # Vercel serverless environment
            self.terminal_root = Path("/var/task/terminal_root") if os.path.exists("/var/task/terminal_root") else Path("/tmp/terminal_root")
        elif os.path.exists("/app"):
            # Docker/container environment
            self.terminal_root = Path("/app/terminal_root")
        else:
            # Local development
            self.terminal_root = Path.cwd().parent / "terminal_root"
        
        # Create terminal_root if it doesn't exist (for Vercel /tmp)
        try:
            if not self.terminal_root.exists():
                self.terminal_root.mkdir(parents=True, exist_ok=True)
                # Create subdirectories
                for subdir in ["home", "documents", "downloads", "projects"]:
                    (self.terminal_root / subdir).mkdir(exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create terminal_root at {self.terminal_root}: {e}")
            # Fallback to /tmp if creation fails
            self.terminal_root = Path("/tmp/terminal_root")
            try:
                self.terminal_root.mkdir(parents=True, exist_ok=True)
                for subdir in ["home", "documents", "downloads", "projects"]:
                    (self.terminal_root / subdir).mkdir(exist_ok=True)
            except Exception as e2:
                print(f"Error: Could not create fallback terminal_root: {e2}")
        
        self.current_dir = self.terminal_root
        print(f"Command processor initialized in: {self.current_dir}")

    def execute(self, cmd: str) -> str:
        if not cmd or not cmd.strip():
            return ""
        
        parts = shlex.split(cmd.strip())
        if not parts:
            return ""
            
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # Check if command is supported
        if command not in COMMANDS:
            return f"Command not found: {command}. Type 'help' for available commands."

        # Try to find the command handler
        handler_method = getattr(self, f"cmd_{command}", None)
        if handler_method:
            try:
                result = handler_method(args)
                return result if result is not None else ""
            except Exception as e:
                print(f"Error in {command}: {e}")  # Debug logging
                return f"Error running {command}: {str(e)}"
        else:
            return f"Handler for '{command}' not implemented yet."

    # ---------- File and Directory Operations ----------

    def cmd_ls(self, args):
        try:
            items = os.listdir(self.current_dir)
            if not items:
                return "(empty directory)"
            
            # Add file type indicators
            formatted_items = []
            for item in sorted(items):
                item_path = self.current_dir / item
                if item_path.is_dir():
                    formatted_items.append(f"{item}/")
                elif item_path.is_file():
                    formatted_items.append(item)
                else:
                    formatted_items.append(item)
            
            return "\n".join(formatted_items)
        except PermissionError:
            return "Permission denied"
        except Exception as e:
            return f"Error listing directory: {e}"

    def cmd_cd(self, args):
        if not args:
            # Go to home directory if no args
            self.current_dir = self.terminal_root / "home"
            return f"Changed to home directory: {self.current_dir}"
        
        target = args[0]
        if target == "..":
            # Go up one level, but don't go above terminal root
            if self.current_dir != self.terminal_root:
                self.current_dir = self.current_dir.parent
            return f"Changed to parent directory: {self.current_dir}"
        elif target == "~":
            self.current_dir = self.terminal_root / "home"
            return f"Changed to home directory: {self.current_dir}"
        
        new_path = (self.current_dir / target).resolve()
        # Ensure we don't go outside terminal root
        if str(new_path).startswith(str(self.terminal_root)) and new_path.exists() and new_path.is_dir():
            self.current_dir = new_path
            return f"Changed to: {self.current_dir.relative_to(self.terminal_root)}"
        else:
            return f"Directory not found: {target}"

    def cmd_pwd(self, args):
        return str(self.current_dir.relative_to(self.terminal_root))

    def cmd_mkdir(self, args):
        if not args:
            return "mkdir: missing operand"
        
        dirname = args[0]
        try:
            new_dir = self.current_dir / dirname
            new_dir.mkdir(parents=True, exist_ok=False)
            return f"Created directory: {dirname}"
        except FileExistsError:
            return f"Directory already exists: {dirname}"
        except PermissionError:
            return f"Permission denied: cannot create directory {dirname}"

    def cmd_rm(self, args):
        if not args:
            return "rm: missing operand"
        
        filename = args[0]
        target = self.current_dir / filename
        try:
            if target.is_file():
                target.unlink()
                return f"Removed file: {filename}"
            elif target.is_dir():
                return f"rm: {filename} is a directory (use rmdir or rm -r)"
            else:
                return f"rm: cannot remove '{filename}': No such file or directory"
        except PermissionError:
            return f"rm: cannot remove '{filename}': Permission denied"

    def cmd_rmdir(self, args):
        if not args:
            return "rmdir: missing operand"
        
        dirname = args[0]
        target = self.current_dir / dirname
        try:
            if target.is_dir():
                os.rmdir(target)  # Only removes empty directories
                return f"Removed directory: {dirname}"
            else:
                return f"rmdir: failed to remove '{dirname}': Not a directory"
        except OSError as e:
            return f"rmdir: failed to remove '{dirname}': {e}"

    def cmd_touch(self, args):
        if not args:
            return "touch: missing operand"
        
        filename = args[0]
        try:
            (self.current_dir / filename).touch(exist_ok=True)
            return f"Created/updated file: {filename}"
        except PermissionError:
            return f"touch: cannot touch '{filename}': Permission denied"

    def cmd_cat(self, args):
        if not args:
            return "Usage: cat <file>"
        file = self.current_dir / args[0]
        if file.is_file():
            return file.read_text()
        return f"No such file: {args[0]}"

    def cmd_echo(self, args):
        return " ".join(args)

    def cmd_clear(self, args):
        return "<CLEAR_SCREEN>"

    def cmd_mv(self, args):
        if len(args) != 2:
            return "Usage: mv <src> <dest>"
        src = self.current_dir / args[0]
        dst = self.current_dir / args[1]
        shutil.move(src, dst)
        return f"Moved '{args[0]}' to '{args[1]}'"

    def cmd_cp(self, args):
        if len(args) != 2:
            return "Usage: cp <src> <dest>"
        src = self.current_dir / args[0]
        dst = self.current_dir / args[1]
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
        return f"Copied '{args[0]}' to '{args[1]}'"

    def cmd_ln(self, args):
        if len(args) < 2:
            return "Usage: ln <target> <link_name>"
        target = self.current_dir / args[0]
        link_name = self.current_dir / args[1]
        try:
            link_name.symlink_to(target)
            return f"Created symbolic link: {args[1]} -> {args[0]}"
        except Exception as e:
            return f"Error creating link: {e}"

    def cmd_chmod(self, args):
        if len(args) < 2:
            return "Usage: chmod <mode> <file>"
        mode, filename = args[0], args[1]
        file_path = self.current_dir / filename
        try:
            os.chmod(file_path, int(mode, 8))
            return f"Changed permissions of {filename} to {mode}"
        except Exception as e:
            return f"Error changing permissions: {e}"

    def cmd_file(self, args):
        if not args:
            return "Usage: file <filename>"
        file_path = self.current_dir / args[0]
        if file_path.exists():
            if file_path.is_dir():
                return f"{args[0]}: directory"
            elif file_path.is_file():
                return f"{args[0]}: regular file"
            else:
                return f"{args[0]}: special file"
        return f"{args[0]}: cannot open"

    def cmd_stat(self, args):
        if not args:
            return "Usage: stat <file>"
        file_path = self.current_dir / args[0]
        if file_path.exists():
            stat_info = file_path.stat()
            return f"File: {args[0]}\nSize: {stat_info.st_size} bytes\nModified: {time.ctime(stat_info.st_mtime)}"
        return f"stat: cannot stat '{args[0]}': No such file or directory"

    # ---------- Text Processing ----------

    def cmd_head(self, args):
        if not args:
            return "Usage: head <file>"
        file = self.current_dir / args[0]
        if file.is_file():
            lines = file.read_text().splitlines()
            return "\n".join(lines[:10])
        return f"No such file: {args[0]}"

    def cmd_tail(self, args):
        if not args:
            return "Usage: tail <file>"
        file = self.current_dir / args[0]
        if file.is_file():
            lines = file.read_text().splitlines()
            return "\n".join(lines[-10:])
        return f"No such file: {args[0]}"

    def cmd_grep(self, args):
        if len(args) < 2:
            return "Usage: grep <pattern> <file>"
        pattern, filename = args[0], args[1]
        file = self.current_dir / filename
        if file.is_file():
            lines = file.read_text().splitlines()
            matches = [f"{i+1}:{line}" for i, line in enumerate(lines) if pattern in line]
            return "\n".join(matches) if matches else "(no matches)"
        return f"No such file: {filename}"

    def cmd_sort(self, args):
        if not args:
            return "Usage: sort <file>"
        file = self.current_dir / args[0]
        if file.is_file():
            lines = file.read_text().splitlines()
            return "\n".join(sorted(lines))
        return f"No such file: {args[0]}"

    def cmd_uniq(self, args):
        if not args:
            return "Usage: uniq <file>"
        file = self.current_dir / args[0]
        if file.is_file():
            lines = file.read_text().splitlines()
            unique_lines = []
            prev_line = None
            for line in lines:
                if line != prev_line:
                    unique_lines.append(line)
                    prev_line = line
            return "\n".join(unique_lines)
        return f"No such file: {args[0]}"

    def cmd_wc(self, args):
        if not args:
            return "Usage: wc <file>"
        file = self.current_dir / args[0]
        if file.is_file():
            content = file.read_text()
            lines = len(content.splitlines())
            words = len(content.split())
            chars = len(content)
            return f"{lines} {words} {chars} {args[0]}"
        return f"No such file: {args[0]}"

    def cmd_cut(self, args):
        if len(args) < 2:
            return "Usage: cut -d<delimiter> -f<field> <file>"
        # Simple implementation - cut by spaces
        file = self.current_dir / args[-1]
        if file.is_file():
            lines = file.read_text().splitlines()
            result = []
            for line in lines:
                fields = line.split()
                if len(fields) > 0:
                    result.append(fields[0])  # First field
            return "\n".join(result)
        return f"No such file: {args[-1]}"

    # ---------- System Information ----------

    def cmd_whoami(self, args):
        return "terminal_user"

    def cmd_date(self, args):
        return time.strftime("%a %b %d %H:%M:%S %Z %Y")

    def cmd_uptime(self, args):
        return f"up {int(time.time() / 3600)} hours"

    def cmd_uname(self, args):
        return f"{platform.system()} {platform.release()} {platform.machine()}"

    def cmd_df(self, args):
        return "Filesystem     1K-blocks    Used Available Use% Mounted on\n/dev/root       1000000   500000    500000  50% /"

    def cmd_du(self, args):
        if not args:
            return "Usage: du <directory>"
        dir_path = self.current_dir / args[0]
        if dir_path.is_dir():
            total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            return f"{total_size // 1024}\t{args[0]}"
        return f"du: cannot access '{args[0]}': No such file or directory"

    def cmd_free(self, args):
        return "              total        used        free      shared  buff/cache   available\nMem:        8000000     4000000     2000000          0     2000000     4000000\nSwap:       2000000           0     2000000"

    def cmd_top(self, args):
        return "PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n1 root      20   0   12345    1234    1234 S   0.0   0.1   0:00.01 init"

    def cmd_ps(self, args):
        return "PID TTY          TIME CMD\n1 ?        00:00:00 init\n2 ?        00:00:00 kthreadd"

    def cmd_kill(self, args):
        if not args:
            return "kill: missing operand"
        return f"Process {args[0]} terminated"

    def cmd_killall(self, args):
        if not args:
            return "killall: missing operand"
        return f"Process {args[0]} terminated"

    def cmd_jobs(self, args):
        return "No jobs running"

    def cmd_bg(self, args):
        return "No jobs to run in background"

    def cmd_fg(self, args):
        return "No jobs to bring to foreground"

    # ---------- Network and Utilities ----------

    def cmd_ping(self, args):
        if not args:
            return "Usage: ping <host>"
        return f"PING {args[0]} (127.0.0.1): 56 data bytes\n64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.1 ms"

    def cmd_curl(self, args):
        if not args:
            return "Usage: curl <url>"
        return f"curl: (6) Could not resolve host: {args[0]}"

    def cmd_wget(self, args):
        if not args:
            return "Usage: wget <url>"
        return f"wget: unable to resolve host address '{args[0]}'"

    def cmd_ssh(self, args):
        return "ssh: connect to host: Connection refused"

    def cmd_scp(self, args):
        return "scp: connect to host: Connection refused"

    def cmd_tar(self, args):
        if not args:
            return "Usage: tar [options] <archive>"
        return f"tar: {args[-1]}: Cannot open: No such file or directory"

    def cmd_zip(self, args):
        if len(args) < 2:
            return "Usage: zip <archive> <files...>"
        return f"zip: {args[0]}: No such file or directory"

    def cmd_unzip(self, args):
        if not args:
            return "Usage: unzip <archive>"
        return f"unzip: cannot find or open {args[0]}, {args[0]}.zip or {args[0]}.ZIP"

    # ---------- Terminal Control ----------

    def cmd_history(self, args):
        return "No history available"

    def cmd_alias(self, args):
        if not args:
            return "No aliases defined"
        return f"Alias '{args[0]}' created"

    def cmd_export(self, args):
        if not args:
            return "No environment variables to export"
        return f"Exported {args[0]}"

    def cmd_env(self, args):
        return "PATH=/usr/bin:/bin\nHOME=/home/terminal_user\nUSER=terminal_user"

    def cmd_which(self, args):
        if not args:
            return "Usage: which <command>"
        if args[0] in COMMANDS:
            return f"/usr/bin/{args[0]}"
        return f"which: no {args[0]} in (/usr/bin:/bin)"

    def cmd_whereis(self, args):
        if not args:
            return "Usage: whereis <command>"
        if args[0] in COMMANDS:
            return f"{args[0]}: /usr/bin/{args[0]}"
        return f"{args[0]}:"

    # ---------- Help and Documentation ----------

    def cmd_help(self, args):
        help_text = "Available commands:\n\n"
        
        # Group commands by category
        categories = {
            "File & Directory Operations": ["ls", "cd", "pwd", "mkdir", "rm", "rmdir", "touch", "cat", "echo", "mv", "cp", "ln", "chmod", "chown", "file", "stat"],
            "Text Processing": ["head", "tail", "grep", "sed", "awk", "sort", "uniq", "wc", "cut"],
            "System Information": ["whoami", "date", "uptime", "uname", "df", "du", "free", "top", "ps", "kill", "killall", "jobs", "bg", "fg"],
            "Network & Utilities": ["ping", "curl", "wget", "ssh", "scp", "tar", "zip", "unzip"],
            "Terminal Control": ["clear", "history", "alias", "export", "env", "which", "whereis"],
            "Help & Documentation": ["help", "man", "info"]
        }
        
        order = [
            "File & Directory Operations",
            "Text Processing",
            "System Information",
            "Network & Utilities",
            "Terminal Control",
            "Help & Documentation"
        ]

        for category in order:
            cmds = categories.get(category, [])
            if not cmds:
                continue
            help_text += f"{category}:\n"
            # Sort commands alphabetically for readability
            for cmd in sorted(cmds):
                if cmd in COMMAND_HELP:
                    help_text += f"  {cmd:<10} - {COMMAND_HELP[cmd]}\n"
            help_text += "\n"
        
        help_text += f"Current directory: {self.current_dir.relative_to(self.terminal_root)}\n"
        help_text += "Tip: Use 'cd ..' to go up one directory level"
        return help_text

    def cmd_man(self, args):
        if not args:
            return "Usage: man <command>"
        if args[0] in COMMAND_HELP:
            return f"Manual page for {args[0]}\n\n{COMMAND_HELP[args[0]]}"
        return f"No manual entry for {args[0]}"

    def cmd_info(self, args):
        if not args:
            return "Usage: info <command>"
        if args[0] in COMMAND_HELP:
            return f"Info: {args[0]}\n\n{COMMAND_HELP[args[0]]}"
        return f"No info entry for {args[0]}"