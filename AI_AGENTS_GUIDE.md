# AI Code Management Agents - User Guide

## Overview

The AI Code Management Agents framework provides automated assistance for:
- **Error Correction**: Detecting and suggesting code fixes
- **Model Training**: Managing ML model updates and retraining
- **GitHub Sync**: Automated Git commits and pushes
- **Code Tracking**: Tracking changes and generating reports

## Architecture

### Components

#### 1. **CodeAnalysisAgent**
Detects code errors and suggests corrections.

**Features:**
- Scans all Python files for errors
- Detects unused imports
- Finds bare except clauses
- Identifies missing docstrings
- Suggests code improvements

**Usage:**
```python
from ai_code_agents import CodeAnalysisAgent

analyzer = CodeAnalysisAgent('.')
errors = analyzer.scan_python_files()
report = analyzer.generate_error_report()
```

#### 2. **ModelTrainingAgent**
Manages ML model training and updates.

**Features:**
- Checks if models need retraining
- Determines model age
- Identifies training triggers
- Executes training scripts
- Maintains training history

**Usage:**
```python
from ai_code_agents import ModelTrainingAgent

trainer = ModelTrainingAgent('.')
needs_update = trainer.check_training_needs()
if needs_update['needs_retraining']:
    result = trainer.retrain_models('train_model.py')
```

#### 3. **GitHubSyncAgent**
Automates Git operations and GitHub synchronization.

**Features:**
- Checks Git status
- Stages changes (selective or all)
- Creates commits with messages
- Pushes to GitHub
- Maintains sync history

**Usage:**
```python
from ai_code_agents import GitHubSyncAgent

git_sync = GitHubSyncAgent('.')
status = git_sync.check_git_status()
git_sync.stage_changes(['file1.py', 'file2.py'])
git_sync.commit_changes("Update: Fixed bugs")
git_sync.push_to_github('main')
```

#### 4. **CodeChangeTracker**
Tracks code changes and generates summaries.

**Features:**
- Retrieves recent Git commits
- Detects file modifications
- Tracks new/deleted files
- Generates change summaries
- Maintains change history

**Usage:**
```python
from ai_code_agents import CodeChangeTracker

tracker = CodeChangeTracker('.')
recent = tracker.get_recent_changes(limit=10)
changes = tracker.detect_file_changes()
summary = tracker.generate_change_summary()
```

#### 5. **CodeManagementOrchestrator**
Coordinates all agents in a unified pipeline.

**Features:**
- Runs complete management pipeline
- Coordinates all agents
- Generates comprehensive reports
- Saves results to JSON

**Usage:**
```python
from ai_code_agents import CodeManagementOrchestrator

orchestrator = CodeManagementOrchestrator('.')
result = orchestrator.run_full_pipeline(
    auto_commit=True,
    auto_push=True
)
report = orchestrator.generate_report()
```

## Quick Start

### Installation

No additional installation needed beyond the project dependencies.

### Basic Usage

#### Run Test Suite
```powershell
cd C:\Users\hp\Desktop\P_URL_D
venv\Scripts\python.exe test_ai_agents.py
```

#### Run Full Pipeline
```powershell
venv\Scripts\python.exe test_ai_agents.py --full-pipeline
```

#### Interactive Usage
```python
from ai_code_agents import CodeManagementOrchestrator

# Create orchestrator
orchestrator = CodeManagementOrchestrator('.')

# Run full pipeline
result = orchestrator.run_full_pipeline(
    auto_commit=True,
    auto_push=True
)

# Generate report
report = orchestrator.generate_report()

# Save report
orchestrator.save_report('management_report.json')
```

## Workflow

### Complete Workflow

```
1. CODE ANALYSIS
   └─ Scan Python files
   └─ Detect errors (unused imports, bare except, missing docstrings)
   └─ Generate error report

2. MODEL TRAINING CHECK
   └─ Check model age
   └─ Compare with training threshold (30 days)
   └─ Determine if retraining needed

3. GIT STATUS CHECK
   └─ Check current branch
   └─ Detect staged/unstaged changes
   └─ Identify untracked files

4. CHANGE DETECTION
   └─ Get recent commits
   └─ Detect modified files
   └─ Track new/deleted files

5. GITHUB SYNC (Optional)
   └─ Stage changes
   └─ Create commit with auto-message
   └─ Push to GitHub
```

## Output Files

### Generated Reports

#### 1. **ai_agents_report.json**
Comprehensive management report with:
- Code analysis results
- Training status
- Git sync history
- Change summary
- Recent operations

#### 2. **ai_agents_test_results.json**
Test suite results with:
- Individual test outcomes
- Test metrics
- Success rates
- Detailed test information

#### 3. **management_report.json**
Custom report (if generated via orchestrator)

## Advanced Features

### Selective File Staging
```python
git_sync = GitHubSyncAgent('.')
# Stage specific files
git_sync.stage_changes(['file1.py', 'file2.py', 'file3.py'])
```

### Custom Commit Messages
```python
message = "Feat: Add new error detection + Model update"
git_sync.commit_changes(message)
```

### Model Retraining
```python
trainer = ModelTrainingAgent('.')
result = trainer.retrain_models('train_model.py')
if result['success']:
    print("Training completed successfully")
else:
    print(f"Training failed: {result['error']}")
```

### Error Analysis
```python
analyzer = CodeAnalysisAgent('.')
errors = analyzer.scan_python_files()
for file_path, error_list in errors.items():
    print(f"{file_path}: {len(error_list)} errors")
    for error in error_list[:3]:  # First 3 errors
        print(f"  - {error}")
```

## Configuration

### Model Training Thresholds
Edit `ModelTrainingAgent.check_training_needs()`:
```python
# Retrain if model is older than X days
if age_days > 30:  # Change 30 to desired threshold
    analysis['needs_retraining'] = True
```

### Error Detection Rules
Edit `CodeAnalysisAgent._check_file()` to add custom error patterns.

### Git Operations Timeout
Current timeout: 30 seconds for push, 10 seconds for other operations
Edit `GitHubSyncAgent` methods to change timeouts.

## Error Handling

All agents handle errors gracefully:
- Failed operations return detailed error messages
- Exceptions don't crash the pipeline
- All operations logged for debugging

### Example Error Handling
```python
try:
    orchestrator.run_full_pipeline()
except Exception as e:
    print(f"Pipeline error: {str(e)}")
    # Pipeline continues with other agents
```

## Logging and Debugging

### Enable Detailed Output
All agents print status messages to console:
```
[1/5] Analyzing code for errors...
      Found 5 errors in 2 files
[2/5] Checking model training needs...
      Model retraining needed: Model is 45 days old (threshold: 30 days)
...
```

### Access Operation Logs
```python
orchestrator = CodeManagementOrchestrator('.')
result = orchestrator.run_full_pipeline()

# Access logs
for op_name, op_result in result['operations'].items():
    print(f"{op_name}: {op_result}")
```

## Common Use Cases

### Use Case 1: Daily Automated Updates
```python
# Schedule this daily
orchestrator = CodeManagementOrchestrator('.')
result = orchestrator.run_full_pipeline(auto_commit=True, auto_push=True)
orchestrator.save_report('daily_report.json')
```

### Use Case 2: Pre-Deployment Checks
```python
# Run before deploying
analyzer = CodeAnalysisAgent('.')
errors = analyzer.scan_python_files()

if errors:
    print(f"⚠ Found {sum(len(v) for v in errors.values())} errors")
    sys.exit(1)
else:
    print("✓ Code analysis passed")
```

### Use Case 3: Model Management
```python
# Weekly model check
trainer = ModelTrainingAgent('.')
check = trainer.check_training_needs()

if check['needs_retraining']:
    result = trainer.retrain_models()
    if result['success']:
        git_sync = GitHubSyncAgent('.')
        git_sync.stage_changes(['models/'])
        git_sync.commit_changes("Update: Retrained models")
        git_sync.push_to_github()
```

### Use Case 4: Change Tracking Report
```python
# Generate weekly summary
tracker = CodeChangeTracker('.')
summary = tracker.generate_change_summary()

print(f"Week Summary:")
print(f"  Files modified: {summary['files_modified_total']}")
print(f"  New files: {summary['files_created_total']}")
print(f"  Deleted files: {summary['files_deleted_total']}")
```

## Prerequisites

### Git Configuration
Ensure Git is configured with:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### GitHub Credentials
For push operations, ensure GitHub credentials are configured:
- SSH keys, or
- GitHub token in Git credentials

### Project Structure
- Project must be a Git repository (`.git` folder exists)
- Python files should follow standard naming conventions
- Models directory should exist: `models/`

## Troubleshooting

### Issue: "Not a git repository"
**Solution**: Initialize Git in project root
```bash
cd your_project
git init
```

### Issue: "Git push fails"
**Solution**: Check GitHub credentials and network connection
```bash
git push origin main --dry-run  # Test connection
```

### Issue: "Model training times out"
**Solution**: Increase timeout in `ModelTrainingAgent.retrain_models()`
```python
process = subprocess.run(..., timeout=600)  # 10 minutes
```

### Issue: "Permission denied on push"
**Solution**: Check GitHub SSH keys or use HTTPS credentials

## Best Practices

1. **Run tests regularly**: Use `test_ai_agents.py` to verify functionality
2. **Check reports**: Review generated JSON reports for insights
3. **Schedule operations**: Use task scheduler for automated runs
4. **Monitor history**: Keep sync history records
5. **Version control**: Always commit before major changes

## API Reference

### CodeAnalysisAgent Methods
- `scan_python_files()` → Dict[str, List[str]]
- `suggest_corrections(filepath)` → List[Dict]
- `generate_error_report()` → Dict

### ModelTrainingAgent Methods
- `check_training_needs()` → Dict
- `retrain_models(script_path)` → Dict
- `get_training_status()` → Dict

### GitHubSyncAgent Methods
- `check_git_status()` → Dict
- `stage_changes(files)` → Dict
- `commit_changes(message)` → Dict
- `push_to_github(branch)` → Dict
- `get_sync_history()` → List[Dict]

### CodeChangeTracker Methods
- `get_recent_changes(limit)` → List[Dict]
- `detect_file_changes()` → Dict
- `generate_change_summary()` → Dict

### CodeManagementOrchestrator Methods
- `run_full_pipeline(auto_commit, auto_push)` → Dict
- `generate_report()` → Dict
- `save_report(filename)` → bool

## Performance

### Typical Execution Times
- Code analysis: 2-5 seconds
- Model training check: <1 second
- Git status check: 1-2 seconds
- Change detection: <1 second
- Full pipeline: 5-10 seconds
- Push to GitHub: 5-30 seconds (depending on network)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review generated JSON reports
3. Check console output for error messages
4. Review Git status manually: `git status`

## License

Part of the URL Detection Project AI Management System.
