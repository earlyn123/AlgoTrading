# Define the directory containing the .dbn.zst compressed files
$inputDir = "C:\Users\early\AlgoTrading\BacktestLayer\data\HistoricalPricingData"
# Define the directory to store the intermediate CSV files
$outputDir = "C:\Users\early\AlgoTrading\FakeDataBento\historical_data\csv_files"
# Define the final concatenated CSV file
$finalOutputFile = "C:\Users\early\AlgoTrading\FakeDataBento\historical_data\nyse_data_concatenated.csv"

# Create the output directory if it doesn't exist
if (-Not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir
}

# Remove the final output file if it already exists
if (Test-Path $finalOutputFile) {
    Remove-Item $finalOutputFile
}

# Loop through each .dbn.zst file in the directory
Get-ChildItem -Path $inputDir -Filter *.dbn.zst | ForEach-Object {
    $fileName = $_.BaseName
    $tempFilePath = "$($outputDir)\$fileName.dbn"
    $csvFilePath = "$($outputDir)\$fileName.csv"
    
    # Decompress the .dbn.zst file
    & zstd.exe -d $_.FullName -o $tempFilePath

    # Convert the .dbn file to CSV using a Python script
    python -c "
import databento as db
stored_data = db.from_dbn(r'$tempFilePath')
stored_data.to_csv(r'$csvFilePath')
"
    
    # Remove the temporary .dbn file
    Remove-Item $tempFilePath
}

# Concatenate all CSV files into one, ensuring only the first file has the header row
$csvFiles = Get-ChildItem -Path $outputDir -Filter *.csv
$header = $true

foreach ($csv in $csvFiles) {
    if ($header) {
        Get-Content $csv.FullName | Add-Content $finalOutputFile
        $header = $false
    } else {
        Get-Content $csv.FullName | Select-Object -Skip 1 | Add-Content $finalOutputFile
    }
}

Write-Host "Decompression, conversion, and concatenation completed. Final output file: $finalOutputFile"
