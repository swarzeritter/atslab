*** Settings ***
Library           SeleniumLibrary
Suite Setup       Open Blog
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}    http://127.0.0.1:8000
${BROWSER}     Chrome
${USERNAME}    test1234
${EMAIL}       test@gmail.com
${PASSWORD}    test1234
${POST_TITLE}  Hellow world?

*** Keywords ***
Open Blog
    Open Browser    ${BASE_URL}/posts    ${BROWSER}
    Set Window Size    1373    782

Login With
    [Arguments]    ${email}    ${password}
    Go To    ${BASE_URL}/auth/login
    Input Text    id:email    ${email}
    Input Text    id:password    ${password}
    Click Button    css:.btn-primary

Logout
    Click Element    css:.dropdown-toggle
    Click Link    link:Вийти

Create Post
    [Arguments]    ${title}    ${content}
    Go To    ${BASE_URL}/posts/new
    Input Text    name:title    ${title}
    Input Text    name:content    ${content}
    Click Button    css:.btn-primary

Open Post
    [Arguments]    ${title}
    Go To    ${BASE_URL}/posts
    Click Link    link:${title}

*** Test Cases ***
01 Register New User
    Go To    ${BASE_URL}/auth/register
    Input Text    id:username    ${USERNAME}
    Input Text    id:email       ${EMAIL}
    Input Text    id:password    ${PASSWORD}
    Click Button    css:.btn-primary
    Logout

02 Login Invalid Password
    Go To    ${BASE_URL}/auth/login
    Input Text    id:email       ${EMAIL}
    Input Text    id:password    wrongpassword
    Click Button    css:.btn-primary

03 Login Valid
    Login With    ${EMAIL}    ${PASSWORD}

04 Create Post
    Create Post    ${POST_TITLE}    New Post!

05 View Post
    Open Post    ${POST_TITLE}

06 Add Comment
    Open Post    ${POST_TITLE}
    Input Text      name:content    Nice!!
    Click Button    xpath://button[contains(.,'Відправити')]

07 Edit Post
    Open Post    ${POST_TITLE}
    Click Link      link:Редагувати
    Input Text      name:content    New Post!\nAwesome!
    Click Button    css:.btn-primary

08 View Profile
    Click Element    css:.dropdown-toggle
    Click Link       link:Мій профайл

09 Delete Post
    Open Post    ${POST_TITLE}
    Click Button    css:.btn-outline-danger
    Handle Alert

10 Logout
    Logout
