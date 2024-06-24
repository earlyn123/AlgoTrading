$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir'; python .\ExecutionLayer\execution_layer.py"
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir'; python .\ModelLayer\model_layer.py"
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir'; python .\DataLayer\data_layer.py"
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectDir'; python .\FakeDataBento\fake_bento_layer.py"
