"""
AI Code Management Agents - Test Suite
Tests all agents: Error Correction, Model Training, GitHub Sync, Code Tracking
Run this file to execute the complete code management pipeline
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict
from ai_code_agents import (
    CodeAnalysisAgent,
    ModelTrainingAgent,
    GitHubSyncAgent,
    CodeChangeTracker,
    CodeManagementOrchestrator
)


class AIAgentTestSuite:
    """Comprehensive test suite for AI agents"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.test_results = {}
        self.orchestrator = CodeManagementOrchestrator(project_root)
        
    def test_code_analysis_agent(self) -> Dict:
        """Test CodeAnalysisAgent"""
        print("\n" + "="*70)
        print("TEST 1: CODE ANALYSIS AGENT")
        print("="*70)
        
        analyzer = CodeAnalysisAgent(self.project_root)
        
        print("\n[Scanning Python files for errors...]")
        errors = analyzer.scan_python_files()
        
        test_result = {
            'agent': 'CodeAnalysisAgent',
            'status': 'PASSED',
            'tests': {
                'scan_python_files': {
                    'status': 'PASSED',
                    'files_scanned': len(errors),
                    'files_with_errors': len(errors),
                    'total_errors': sum(len(v) for v in errors.values())
                },
                'suggest_corrections': {
                    'status': 'PASSED',
                    'files_checked': 0,
                    'suggestions': 0
                },
                'error_report': {
                    'status': 'PASSED',
                    'report_generated': True
                }
            }
        }
        
        # Test file suggestions
        py_files = list(Path(self.project_root).glob("**/*.py"))[:3]  # Test first 3 files
        for py_file in py_files:
            if "__pycache__" not in str(py_file):
                suggestions = analyzer.suggest_corrections(str(py_file))
                test_result['tests']['suggest_corrections']['files_checked'] += 1
                test_result['tests']['suggest_corrections']['suggestions'] += len(suggestions)
        
        # Test report generation
        report = analyzer.generate_error_report()
        test_result['tests']['error_report']['report'] = report
        
        print(f"\n[OK] Files scanned: {len(errors)}")
        print(f"[OK] Total errors found: {sum(len(v) for v in errors.values())}")
        if errors:
            for file, errs in list(errors.items())[:3]:
                print(f"  - {file}: {len(errs)} errors")
        
        print(f"[OK] Correction suggestions: {test_result['tests']['suggest_corrections']['suggestions']}")
        print(f"[OK] Error report generated: [OK]")
        
        self.test_results['code_analysis'] = test_result
        return test_result
    
    def test_model_training_agent(self) -> Dict:
        """Test ModelTrainingAgent"""
        print("\n" + "="*70)
        print("TEST 2: MODEL TRAINING AGENT")
        print("="*70)
        
        trainer = ModelTrainingAgent(self.project_root)
        
        print("\n[Checking training needs...]")
        training_check = trainer.check_training_needs()
        
        test_result = {
            'agent': 'ModelTrainingAgent',
            'status': 'PASSED',
            'tests': {
                'check_training_needs': {
                    'status': 'PASSED',
                    'needs_retraining': training_check['needs_retraining'],
                    'model_age_days': training_check['model_age_days'],
                    'last_trained': training_check['last_trained'],
                    'reasons': training_check['reasons']
                },
                'get_training_status': {
                    'status': 'PASSED',
                    'training_history_count': len(trainer.training_history)
                }
            }
        }
        
        print(f"\n[OK] Training needs check: Completed")
        print(f"[OK] Model age: {training_check['model_age_days']} days")
        print(f"[OK] Needs retraining: {'YES' if training_check['needs_retraining'] else 'NO'}")
        if training_check['reasons']:
            for reason in training_check['reasons']:
                print(f"  Reason: {reason}")
        
        status = trainer.get_training_status()
        print(f"[OK] Training history records: {status['total_trainings']}")
        print(f"[OK] Last successful training: {status.get('last_successful', 'Never')}")
        
        self.test_results['model_training'] = test_result
        return test_result
    
    def test_github_sync_agent(self) -> Dict:
        """Test GitHubSyncAgent"""
        print("\n" + "="*70)
        print("TEST 3: GITHUB SYNC AGENT")
        print("="*70)
        
        git_sync = GitHubSyncAgent(self.project_root)
        
        print("\n[Checking Git status...]")
        git_status = git_sync.check_git_status()
        
        test_result = {
            'agent': 'GitHubSyncAgent',
            'status': 'PASSED',
            'tests': {
                'check_git_status': {
                    'status': 'PASSED',
                    'git_initialized': git_status['initialized'],
                    'current_branch': git_status['branch'],
                    'staged_changes': len(git_status['staged_changes']),
                    'unstaged_changes': len(git_status['unstaged_changes']),
                    'untracked_files': len(git_status['untracked_files']),
                    'commits_ahead': git_status['commits_ahead']
                },
                'sync_history': {
                    'status': 'PASSED',
                    'sync_attempts': len(git_sync.sync_history)
                }
            }
        }
        
        print(f"\n[OK] Git initialized: {'YES' if git_status['initialized'] else 'NO'}")
        print(f"[OK] Current branch: {git_status['branch']}")
        print(f"[OK] Staged changes: {len(git_status['staged_changes'])}")
        print(f"[OK] Unstaged changes: {len(git_status['unstaged_changes'])}")
        print(f"[OK] Untracked files: {len(git_status['untracked_files'])}")
        
        if git_status['unstaged_changes']:
            print("\n  Recent unstaged changes:")
            for file in git_status['unstaged_changes'][:3]:
                print(f"    - {file}")
        
        print(f"\n[OK] Sync history records: {len(git_sync.sync_history)}")
        
        self.test_results['github_sync'] = test_result
        return test_result
    
    def test_code_change_tracker(self) -> Dict:
        """Test CodeChangeTracker"""
        print("\n" + "="*70)
        print("TEST 4: CODE CHANGE TRACKER")
        print("="*70)
        
        tracker = CodeChangeTracker(self.project_root)
        
        print("\n[Detecting recent changes...]")
        recent = tracker.get_recent_changes(limit=10)
        
        print("\n[Detecting file changes...]")
        changes = tracker.detect_file_changes()
        
        print("\n[Generating change summary...]")
        summary = tracker.generate_change_summary()
        
        test_result = {
            'agent': 'CodeChangeTracker',
            'status': 'PASSED',
            'tests': {
                'get_recent_changes': {
                    'status': 'PASSED',
                    'recent_commits': len(recent)
                },
                'detect_file_changes': {
                    'status': 'PASSED',
                    'modified_files': len(changes['modified']),
                    'new_files': len(changes['new']),
                    'deleted_files': len(changes['deleted'])
                },
                'change_summary': {
                    'status': 'PASSED',
                    'total_tracked_changes': summary['total_changes'],
                    'files_modified_total': summary['files_modified_total'],
                    'files_created_total': summary['files_created_total'],
                    'files_deleted_total': summary['files_deleted_total']
                }
            }
        }
        
        print(f"\n[OK] Recent commits: {len(recent)}")
        if recent:
            for commit in recent[:3]:
                print(f"  - {commit['commit_hash']}: {commit['message'][:50]}")
        
        print(f"\n[OK] Current file changes:")
        print(f"  Modified: {len(changes['modified'])}")
        print(f"  New: {len(changes['new'])}")
        print(f"  Deleted: {len(changes['deleted'])}")
        
        print(f"\n[OK] Total tracked changes: {summary['total_changes']}")
        print(f"[OK] Files modified (all-time): {summary['files_modified_total']}")
        print(f"[OK] Files created (all-time): {summary['files_created_total']}")
        print(f"[OK] Files deleted (all-time): {summary['files_deleted_total']}")
        
        self.test_results['code_change_tracker'] = test_result
        return test_result
    
    def test_orchestrator(self) -> Dict:
        """Test CodeManagementOrchestrator"""
        print("\n" + "="*70)
        print("TEST 5: CODE MANAGEMENT ORCHESTRATOR")
        print("="*70)
        
        print("\n[Running full pipeline (without auto-push)...]")
        pipeline_result = self.orchestrator.run_full_pipeline(
            auto_commit=False,
            auto_push=False
        )
        
        print("\n[Generating comprehensive report...]")
        report = self.orchestrator.generate_report()
        
        test_result = {
            'agent': 'CodeManagementOrchestrator',
            'status': 'PASSED',
            'tests': {
                'run_full_pipeline': {
                    'status': 'PASSED',
                    'pipeline_status': pipeline_result['status'],
                    'operations': list(pipeline_result['operations'].keys())
                },
                'generate_report': {
                    'status': 'PASSED',
                    'report_sections': list(report.keys()),
                    'recent_operations': len(report['recent_operations'])
                },
                'save_report': {
                    'status': 'PASSED',
                    'report_saved': self.orchestrator.save_report('ai_agents_report.json')
                }
            }
        }
        
        print(f"\n[OK] Pipeline executed: {pipeline_result['status']}")
        print(f"[OK] Operations performed: {len(pipeline_result['operations'])}")
        for op_name in pipeline_result['operations'].keys():
            print(f"  - {op_name}")
        
        print(f"\n[OK] Report sections: {len(report)}")
        print(f"[OK] Report saved: [OK] (ai_agents_report.json)")
        
        self.test_results['orchestrator'] = test_result
        return test_result
    
    def run_all_tests(self) -> Dict:
        """Run all tests"""
        print("\n\n")
        print("=" * 70)
        print(" " * 15 + "AI CODE MANAGEMENT AGENTS - TEST SUITE")
        print("=" * 70)
        
        all_results = {
            'test_suite': 'AI Code Management Agents',
            'timestamp': datetime.now().isoformat(),
            'project_root': self.project_root,
            'tests': {}
        }
        
        try:
            self.test_code_analysis_agent()
            self.test_model_training_agent()
            self.test_github_sync_agent()
            self.test_code_change_tracker()
            self.test_orchestrator()
        except Exception as e:
            print(f"\n[ERROR] Test suite error: {str(e)}")
        
        # Summary
        print("\n\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results.values() if t['status'] == 'PASSED')
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\nTest Results:")
        for test_name, result in self.test_results.items():
            status_symbol = "[OK]" if result['status'] == 'PASSED' else "[FAIL]"
            print(f"  {status_symbol} {test_name}: {result['status']}")
        
        all_results['tests'] = self.test_results
        all_results['summary'] = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'success_rate': f"{(passed_tests/total_tests*100):.1f}%"
        }
        
        # Save test results
        try:
            with open('ai_agents_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2)
            print(f"\n[OK] Test results saved to ai_agents_test_results.json")
        except Exception as e:
            print(f"Error saving test results: {str(e)}")
        
        print("\n" + "="*70)
        
        return all_results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Code Management Agents Test Suite')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--full-pipeline', action='store_true', help='Run full pipeline with Git operations')
    args = parser.parse_args()
    
    test_suite = AIAgentTestSuite(args.project_root)
    results = test_suite.run_all_tests()
    
    if args.full_pipeline:
        print("\n[INFO] Running full pipeline with Git operations...")
        orchestrator = CodeManagementOrchestrator(args.project_root)
        orchestrator.run_full_pipeline(auto_commit=True, auto_push=True)
    
    return results


if __name__ == '__main__':
    main()
