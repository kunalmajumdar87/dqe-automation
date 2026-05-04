*** Settings ***
Library           SeleniumLibrary
Library           helper.Helper

*** Variables ***
${REPORT_FILE}        C:/Users/KunalMajumdar/OneDrive - EPAM/GIT Epam/Personal/dqe-automation/PyTest DQ Framework/reports/report.html
${PARQUET_FOLDER}     C:/Users/KunalMajumdar/OneDrive - EPAM/GIT Epam/Personal/dqe-automation/parquet_data
${FILTER_DATE}        2024-01-01

*** Test Cases ***
Compare HTML Table and Parquet Data
    Open Browser    file://${REPORT_FILE}    Chrome
    ${table}=    Get WebElement    //table
    ${table_html}=    Get Element Attribute    ${table}    outerHTML
    ${html_df}=    Read Html Table To Df    ${table_html}
    ${parquet_df}=    Read Parquet With Filter    ${PARQUET_FOLDER}    ${FILTER_DATE}    visit_date
    ${result}    ${diff}=    Compare Dataframes    ${html_df}    ${parquet_df}
    Run Keyword If    '${result}'=='True'    Log    Data matches!
    Run Keyword If    '${result}'=='False'    Fail    Data mismatch: ${diff}
    [Teardown]    Close Browser