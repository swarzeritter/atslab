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
    Wait Until Element Is Visible    id:email    10s
    Execute Javascript    document.querySelector('#email').value = '${email}'
    Execute Javascript    document.querySelector('#password').value = '${password}'
    Execute Javascript    document.querySelector('form').submit()
    Wait Until Location Contains    posts    10s

Logout
    Go To    ${BASE_URL}/auth/logout
    Wait Until Location Contains    posts    10s

Create Post
    [Arguments]    ${title}    ${content}
    Go To    ${BASE_URL}/posts/new
    Wait Until Element Is Visible    css=input[name='title']    10s
    Execute Javascript    document.querySelector("input[name='title']").value = '${title}'
    Execute Javascript    document.querySelector("textarea[name='content']").value = '${content}'
    Execute Javascript    document.querySelector("form").submit()
    Wait Until Location Contains    /posts/    10s

Open Post
    [Arguments]    ${title}
    Go To    ${BASE_URL}/posts
    Wait Until Element Is Visible    css=.card-title a    10s
    Execute Javascript    document.querySelector('.card-title a').click()
    Wait Until Element Is Visible    css=article    10s

*** Test Cases ***
01 Register New User
    Go To    ${BASE_URL}/auth/register
    Wait Until Element Is Visible    id:username    10s
    Execute Javascript    document.querySelector('#username').value = '${USERNAME}'
    Execute Javascript    document.querySelector('#email').value = '${EMAIL}'
    Execute Javascript    document.querySelector('#password').value = '${PASSWORD}'
    Execute Javascript    document.querySelector('form').submit()
    Wait Until Location Contains    posts    10s
    Logout

02 Login Invalid Password
    Go To    ${BASE_URL}/auth/login
    Wait Until Element Is Visible    id:email    10s
    Execute Javascript    document.querySelector('#email').value = '${EMAIL}'
    Execute Javascript    document.querySelector('#password').value = 'wrongpassword'
    Execute Javascript    document.querySelector('form').submit()

03 Login Valid
    Login With    ${EMAIL}    ${PASSWORD}

04 Create Post
    Create Post    ${POST_TITLE}    New Post!

05 View Post
    Open Post    ${POST_TITLE}

06 Add Comment
    Open Post    ${POST_TITLE}
    Input Text      name:content    Nice!!
    Click Button    css:#comments .btn-primary

07 Edit Post
    Open Post    ${POST_TITLE}
    Execute Javascript    document.querySelector('a[href*="/posts/"][href*="/edit"]').click()
    Wait Until Element Is Visible    css=textarea[name='content']    10s
    Execute Javascript    document.querySelector("textarea[name='content']").value = 'New Post! Awesome!'
    Execute Javascript    document.querySelector('form').submit()

08 View Profile
    Go To    ${BASE_URL}/profile/${USERNAME}

09 Delete Post
    Open Post    ${POST_TITLE}
    Wait Until Element Is Visible    css=.btn-outline-danger    10s
    Execute Javascript    document.querySelector('.btn-outline-danger').closest('form').onsubmit = null
    Click Button    css=.btn-outline-danger

10 Logout
    Logout
