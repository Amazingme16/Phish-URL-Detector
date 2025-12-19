"""
AI Agents Framework for Code Management
Handles: Error correction, model training, GitHub sync, code change tracking
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re


class CodeAnalysisAgent:
    """AI Agent for detecting and correcting code errors"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.error_log = []
        self.corrections = []
        
    def scan_python_files(self) -> Dict[str, List[str]]:
        """Scan all Python files for errors"""
        errors_found = {}
        python_files = Path(self.project_root).glob("**/*.py")
        
        for file_path in python_files:
            if "__pycache__" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                errors = self._check_file(str(file_path), content)
                if errors:
                    errors_found[str(file_path)] = errors
                    self.error_log.append({
                        'file': str(file_path),
                        'errors': errors,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
        
        return errors_found
    
    def _check_file(self, filepath: str, content: str) -> List[str]:
        """Check individual file for common errors"""
        errors = []
        lines = content.split('\n')
        
        # Check for common Python errors
        for i, line in enumerate(lines, 1):
            # Unused imports
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                module = line.split()[1]
                if module not in content:
                    errors.append(f"Line {i}: Unused import '{module}'")
            
            # Missing except clauses
            if 'except:' in line and 'except Exception' not in line:
                errors.append(f"Line {i}: Bare except clause (should specify exception type)")
            
            # TODO comments
            if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                errors.append(f"Line {i}: {line.strip()}")
            
            # Missing docstrings
            if line.strip().startswith('def ') and 'test_' not in line:
                next_line = lines[i].strip() if i < len(lines) else ''
                if not next_line.startswith('"""') and not next_line.startswith("'''"):
                    errors.append(f"Line {i}: Missing docstring for function")
        
        return errors
    
    def suggest_corrections(self, filepath: str) -> List[Dict]:
        """Suggest corrections for a file"""
        suggestions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Common correction patterns
            corrections_map = [
                {
                    'pattern': r'except:\s*',
                    'replacement': 'except Exception as e:',
                    'description': 'Fix bare except clause'
                },
                {
                    'pattern': r'print\(.*?\)',
                    'check': 'Use logging instead of print',
                    'description': 'Replace print with logging'
                }
            ]
            
            for correction in corrections_map:
                if 'pattern' in correction:
                    matches = re.findall(correction['pattern'], content)
                    if matches:
                        suggestions.append({
                            'type': correction['description'],
                            'pattern': correction['pattern'],
                            'replacement': correction.get('replacement', ''),
                            'count': len(matches)
                        })
        except Exception as e:
            print(f"Error suggesting corrections: {str(e)}")
        
        return suggestions
    
    def generate_error_report(self) -> Dict:
        """Generate comprehensive error report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_errors': len(self.error_log),
            'files_scanned': len(set(e['file'] for e in self.error_log)),
            'errors_by_file': self.error_log,
            'corrections_made': self.corrections
        }


class ModelTrainingAgent:
    """AI Agent for managing model training and updates"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.training_history = []
        self.model_metrics = {}
        
    def check_training_needs(self) -> Dict:
        """Check if model retraining is needed"""
        analysis = {
            'needs_retraining': False,
            'reasons': [],
            'last_trained': None,
            'model_age_days': 0
        }
        
        try:
            model_files = [
                os.path.join(self.project_root, 'models', 'lr_model.pkl'),
                os.path.join(self.project_root, 'models', 'rf_model.pkl')
            ]
            
            for model_file in model_files:
                if os.path.exists(model_file):
                    mod_time = os.path.getmtime(model_file)
                    mod_datetime = datetime.fromtimestamp(mod_time)
                    age_days = (datetime.now() - mod_datetime).days
                    
                    analysis['last_trained'] = mod_datetime.isoformat()
                    analysis['model_age_days'] = age_days
                    
                    # Retrain if model is older than 30 days
                    if age_days > 30:
                        analysis['needs_retraining'] = True
                        analysis['reasons'].append(f"Model is {age_days} days old (threshold: 30 days)")
            
            # Check if training script exists and is newer than models
            train_script = os.path.join(self.project_root, 'train_model.py')
            if os.path.exists(train_script):
                train_mod_time = os.path.getmtime(train_script)
                if model_files[0] and os.path.exists(model_files[0]):
                    if train_mod_time > os.path.getmtime(model_files[0]):
                        analysis['needs_retraining'] = True
                        analysis['reasons'].append("Training script has been updated")
        
        except Exception as e:
            print(f"Error checking training needs: {str(e)}")
        
        return analysis
    
    def retrain_models(self, script_path: str = "train_model.py") -> Dict:
        """Execute model retraining"""
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'output': '',
            'error': ''
        }
        
        try:
            full_path = os.path.join(self.project_root, script_path)
            if not os.path.exists(full_path):
                result['error'] = f"Training script not found: {full_path}"
                return result
            
            print(f"[Agent] Starting model retraining from {script_path}...")
            process = subprocess.run(
                ['python', full_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
            if result['success']:
                self.training_history.append({
                    'timestamp': result['timestamp'],
                    'status': 'success',
                    'output': process.stdout[:500]  # First 500 chars
                })
                print(f"[Agent] Model retraining completed successfully")
            else:
                self.training_history.append({
                    'timestamp': result['timestamp'],
                    'status': 'failed',
                    'error': process.stderr[:500]
                })
                print(f"[Agent] Model retraining failed: {process.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            result['error'] = "Training process timed out (exceeded 5 minutes)"
            print("[Agent] Training process timed out")
        except Exception as e:
            result['error'] = str(e)
            print(f"[Agent] Error during retraining: {str(e)}")
        
        return result
    
    def get_training_status(self) -> Dict:
        """Get current training status"""
        return {
            'training_history': self.training_history[-10:],  # Last 10 trainings
            'total_trainings': len(self.training_history),
            'last_successful': next(
                (t['timestamp'] for t in reversed(self.training_history) if t['status'] == 'success'),
                None
            ),
            'model_metrics': self.model_metrics
        }


class GitHubSyncAgent:
    """AI Agent for GitHub synchronization"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.sync_history = []
        
    def check_git_status(self) -> Dict:
        """Check current Git status"""
        status = {
            'initialized': False,
            'branch': None,
            'staged_changes': [],
            'unstaged_changes': [],
            'untracked_files': [],
            'commits_ahead': 0
        }
        
        try:
            git_dir = os.path.join(self.project_root, '.git')
            if not os.path.exists(git_dir):
                return status
            
            status['initialized'] = True
            
            # Get current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            status['branch'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if not line.strip():
                        continue
                    if line.startswith('??'):
                        status['untracked_files'].append(line[3:].strip())
                    elif line.startswith('A'):
                        status['staged_changes'].append(line[3:].strip())
                    else:
                        status['unstaged_changes'].append(line[3:].strip())
        
        except Exception as e:
            print(f"Error checking Git status: {str(e)}")
        
        return status
    
    def stage_changes(self, files: Optional[List[str]] = None) -> Dict:
        """Stage changes for commit"""
        result = {
            'success': False,
            'staged_count': 0,
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if files:
                # Stage specific files
                for file_path in files:
                    subprocess.run(
                        ['git', 'add', file_path],
                        cwd=self.project_root,
                        capture_output=True,
                        timeout=10
                    )
                result['staged_count'] = len(files)
                result['message'] = f"Staged {len(files)} files"
            else:
                # Stage all changes
                subprocess.run(
                    ['git', 'add', '.'],
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=10
                )
                status = self.check_git_status()
                result['staged_count'] = len(status['unstaged_changes']) + len(status['untracked_files'])
                result['message'] = "Staged all changes"
            
            result['success'] = True
        except Exception as e:
            result['message'] = f"Error staging changes: {str(e)}"
            print(f"[Agent] Error staging changes: {str(e)}")
        
        return result
    
    def commit_changes(self, message: str) -> Dict:
        """Commit staged changes"""
        result = {
            'success': False,
            'commit_hash': '',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            proc = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if proc.returncode == 0:
                result['success'] = True
                result['commit_hash'] = proc.stdout.strip()
                print(f"[Agent] Committed: {message}")
            else:
                result['message'] = proc.stderr.strip()
                print(f"[Agent] Commit failed: {proc.stderr}")
        except Exception as e:
            result['message'] = f"Error committing: {str(e)}"
            print(f"[Agent] Error committing: {str(e)}")
        
        return result
    
    def push_to_github(self, branch: str = "main") -> Dict:
        """Push changes to GitHub"""
        result = {
            'success': False,
            'branch': branch,
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            proc = subprocess.run(
                ['git', 'push', 'origin', branch],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if proc.returncode == 0:
                result['success'] = True
                result['message'] = f"Successfully pushed to {branch}"
                print(f"[Agent] Pushed to GitHub: {branch}")
            else:
                result['message'] = proc.stderr.strip()
                print(f"[Agent] Push failed: {proc.stderr}")
        except Exception as e:
            result['message'] = f"Error pushing: {str(e)}"
            print(f"[Agent] Error pushing to GitHub: {str(e)}")
        
        self.sync_history.append(result)
        return result
    
    def get_sync_history(self) -> List[Dict]:
        """Get GitHub sync history"""
        return self.sync_history[-20:]  # Last 20 sync attempts


class CodeChangeTracker:
    """AI Agent for tracking code changes"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.change_log = []
        self.change_summary = {}
        
    def get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Get recent Git commits"""
        changes = []
        
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', f'-{limit}'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        changes.append({
                            'commit_hash': parts[0],
                            'message': parts[1] if len(parts) > 1 else '',
                        })
        except Exception as e:
            print(f"Error getting recent changes: {str(e)}")
        
        return changes
    
    def detect_file_changes(self) -> Dict:
        """Detect which files have changed"""
        changes = {
            'modified': [],
            'new': [],
            'deleted': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Get diff
            result = subprocess.run(
                ['git', 'diff', '--name-status'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                status, filename = line.split('\t', 1)
                if status == 'M':
                    changes['modified'].append(filename)
                elif status == 'A':
                    changes['new'].append(filename)
                elif status == 'D':
                    changes['deleted'].append(filename)
        
        except Exception as e:
            print(f"Error detecting file changes: {str(e)}")
        
        self.change_log.append(changes)
        return changes
    
    def generate_change_summary(self) -> Dict:
        """Generate summary of all tracked changes"""
        summary = {
            'total_changes': len(self.change_log),
            'recent_changes': self.change_log[-5:] if self.change_log else [],
            'files_modified_total': 0,
            'files_created_total': 0,
            'files_deleted_total': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for change in self.change_log:
            summary['files_modified_total'] += len(change['modified'])
            summary['files_created_total'] += len(change['new'])
            summary['files_deleted_total'] += len(change['deleted'])
        
        return summary


class CodeManagementOrchestrator:
    """Main orchestrator for all code management agents"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.code_analyzer = CodeAnalysisAgent(project_root)
        self.model_trainer = ModelTrainingAgent(project_root)
        self.github_sync = GitHubSyncAgent(project_root)
        self.change_tracker = CodeChangeTracker(project_root)
        self.operation_log = []
        
    def run_full_pipeline(self, auto_commit: bool = True, auto_push: bool = True) -> Dict:
        """Run complete code management pipeline"""
        pipeline_result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'operations': {},
            'summary': ''
        }
        
        print("\n" + "="*70)
        print("STARTING CODE MANAGEMENT PIPELINE")
        print("="*70)
        
        # Step 1: Code Analysis
        print("\n[1/5] Analyzing code for errors...")
        errors = self.code_analyzer.scan_python_files()
        pipeline_result['operations']['code_analysis'] = {
            'status': 'completed',
            'files_scanned': len(errors),
            'errors_found': sum(len(v) for v in errors.values()),
            'details': errors
        }
        print(f"      Found {sum(len(v) for v in errors.values())} errors in {len(errors)} files")
        
        # Step 2: Check Training Needs
        print("\n[2/5] Checking model training needs...")
        training_check = self.model_trainer.check_training_needs()
        pipeline_result['operations']['training_check'] = training_check
        if training_check['needs_retraining']:
            print(f"      Model retraining needed: {', '.join(training_check['reasons'])}")
        else:
            print(f"      Models are up to date (age: {training_check['model_age_days']} days)")
        
        # Step 3: Git Status
        print("\n[3/5] Checking Git status...")
        git_status = self.github_sync.check_git_status()
        pipeline_result['operations']['git_status'] = git_status
        print(f"      Branch: {git_status['branch']}")
        print(f"      Changes: {len(git_status['unstaged_changes'])} unstaged, "
              f"{len(git_status['untracked_files'])} untracked")
        
        # Step 4: Detect Changes
        print("\n[4/5] Detecting code changes...")
        changes = self.change_tracker.detect_file_changes()
        pipeline_result['operations']['changes_detected'] = changes
        print(f"      Modified: {len(changes['modified'])}, "
              f"New: {len(changes['new'])}, "
              f"Deleted: {len(changes['deleted'])}")
        
        # Step 5: GitHub Sync (if there are changes)
        print("\n[5/5] Syncing with GitHub...")
        if git_status['unstaged_changes'] or git_status['untracked_files']:
            if auto_commit:
                # Stage changes
                stage_result = self.github_sync.stage_changes()
                pipeline_result['operations']['staging'] = stage_result
                print(f"      Staged {stage_result['staged_count']} items")
                
                # Generate commit message
                commit_msg = f"Auto-update: Code analysis and model check [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
                if training_check['needs_retraining']:
                    commit_msg += " + Model retraining"
                
                # Commit
                commit_result = self.github_sync.commit_changes(commit_msg)
                pipeline_result['operations']['commit'] = commit_result
                
                if auto_push:
                    push_result = self.github_sync.push_to_github()
                    pipeline_result['operations']['push'] = push_result
            else:
                print("      No auto-commit enabled")
        else:
            print("      No changes to sync")
        
        print("\n" + "="*70)
        print("PIPELINE COMPLETED")
        print("="*70 + "\n")
        
        self.operation_log.append(pipeline_result)
        return pipeline_result
    
    def generate_report(self) -> Dict:
        """Generate comprehensive management report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'project_root': self.project_root,
            'code_analysis': self.code_analyzer.generate_error_report(),
            'training_status': self.model_trainer.get_training_status(),
            'git_sync_history': self.github_sync.get_sync_history(),
            'change_summary': self.change_tracker.generate_change_summary(),
            'recent_operations': self.operation_log[-5:] if self.operation_log else []
        }
        
        return report
    
    def save_report(self, filename: str = "management_report.json"):
        """Save comprehensive report to file"""
        report = self.generate_report()
        filepath = os.path.join(self.project_root, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            print(f"[Agent] Report saved to {filepath}")
            return True
        except Exception as e:
            print(f"[Agent] Error saving report: {str(e)}")
            return False


if __name__ == '__main__':
    print("AI Code Management Agents Framework")
    print("This module provides agents for code management tasks")
    print("\nUsage:")
    print("  from ai_code_agents import CodeManagementOrchestrator")
    print("  orchestrator = CodeManagementOrchestrator('.')")
    print("  result = orchestrator.run_full_pipeline()")
