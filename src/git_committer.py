import subprocess
from datetime import datetime
from typing import Dict, Tuple

class GitCommitter:
    """Auto-commit generated tests to Git"""
    
    @staticmethod
    def is_git_repo() -> bool:
        """Check if current directory is a git repo"""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                          capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def init_repo() -> Tuple[bool, str]:
        """Initialize git repo if not exists"""
        try:
            subprocess.run(['git', 'init'], capture_output=True, check=True)
            return True, "Git repo initialized"
        except Exception as e:
            return False, f"Failed to init repo: {str(e)}"
    
    @staticmethod
    def add_files(file_patterns: list) -> Tuple[bool, str]:
        """Add files to git staging"""
        try:
            for pattern in file_patterns:
                subprocess.run(['git', 'add', pattern], 
                              capture_output=True, check=True)
            return True, f"Added {len(file_patterns)} file(s)"
        except Exception as e:
            return False, f"Failed to add files: {str(e)}"
    
    @staticmethod
    def commit(message: str = None) -> Tuple[bool, str]:
        """Commit staged changes"""
        if not message:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"AI-generated tests - {timestamp}"
        
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"Committed: {message}"
        except subprocess.CalledProcessError as e:
            if 'nothing to commit' in e.stdout:
                return True, "No changes to commit"
            return False, f"Commit failed: {e.stderr}"
    
    @staticmethod
    def push(remote: str = 'origin', branch: str = 'main') -> Tuple[bool, str]:
        """Push commits to remote"""
        try:
            subprocess.run(
                ['git', 'push', remote, branch],
                capture_output=True,
                check=True
            )
            return True, f"Pushed to {remote}/{branch}"
        except Exception as e:
            return False, f"Push failed: {str(e)}"
    
    @classmethod
    def auto_commit_tests(cls, test_file_path: str) -> Dict:
        """Auto-commit generated test file"""
        print("\n📝 Auto-committing to Git...")
        
        results = {}
        
        # Check/init repo
        if not cls.is_git_repo():
            success, msg = cls.init_repo()
            results['init'] = (success, msg)
            print(f"  Init: {msg}")
        
        # Add test file
        success, msg = cls.add_files([test_file_path])
        results['add'] = (success, msg)
        print(f"  Add: {msg}")
        
        if not success:
            return results
        
        # Commit
        success, msg = cls.commit()
        results['commit'] = (success, msg)
        print(f"  Commit: {msg}")
        
        # Note: Push requires remote setup, skip for POC
        # Can be enabled later
        
        return results

if __name__ == '__main__':
    # Test git operations
    committer = GitCommitter()
    print("Git repo?", committer.is_git_repo())