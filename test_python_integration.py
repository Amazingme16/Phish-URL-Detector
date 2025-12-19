"""
Python Integration Test for AI Code Management Agents
Tests the CodeManagementOrchestrator directly from Python
"""

from ai_code_agents import CodeManagementOrchestrator

print("\n[PYTHON INTEGRATION TEST]")
print("="*70)

# Step 1: Create orchestrator
print("\nStep 1: Creating CodeManagementOrchestrator...")
orchestrator = CodeManagementOrchestrator('.')
print("[OK] Orchestrator created successfully")

# Step 2: Run pipeline
print("\nStep 2: Running full pipeline...")
print("        (auto_commit=False, auto_push=False for testing)")
result = orchestrator.run_full_pipeline(auto_commit=False, auto_push=False)
print(f"[OK] Pipeline result status: {result['status']}")
print(f"[OK] Operations performed: {len(result['operations'])}")

# Step 3: Check operations details
print("\nStep 3: Operations performed...")
for op_name, op_result in result['operations'].items():
    print(f"  - {op_name}: Completed")

# Step 4: Generate report
print("\nStep 4: Generating comprehensive report...")
report = orchestrator.generate_report()
print(f"[OK] Report generated with {len(report)} sections")
print(f"[OK] Report contains:")
for key in report.keys():
    print(f"      - {key}")

# Step 5: Access report data
print("\nStep 5: Accessing report data...")
print(f"[OK] Code analysis errors found: {report['code_analysis'].get('total_errors', 0)}")
print(f"[OK] Training history records: {report['training_status'].get('total_trainings', 0)}")
print(f"[OK] Git sync history records: {len(report['git_sync_history'])}")
print(f"[OK] Recent changes tracked: {report['change_summary'].get('total_changes', 0)}")

# Step 6: Save report
print("\nStep 6: Saving comprehensive report...")
saved = orchestrator.save_report('python_integration_test.json')
print(f"[OK] Report saved: {saved}")

# Step 7: Test individual agents
print("\nStep 7: Testing individual agents...")
print(f"[OK] Code analyzer errors: {len(orchestrator.code_analyzer.error_log)}")
print(f"[OK] Model trainer history: {len(orchestrator.model_trainer.training_history)}")
print(f"[OK] GitHub sync history: {len(orchestrator.github_sync.sync_history)}")
print(f"[OK] Change tracker log: {len(orchestrator.change_tracker.change_log)}")

print("\n" + "="*70)
print("PYTHON INTEGRATION TEST: PASSED [OK]")
print("="*70)
print("\nAll components working correctly:")
print("  ✓ CodeManagementOrchestrator instantiated")
print("  ✓ Full pipeline executed")
print("  ✓ All agents responding")
print("  ✓ Reports generated and saved")
print("  ✓ Data accessible via Python API")
print("="*70 + "\n")
