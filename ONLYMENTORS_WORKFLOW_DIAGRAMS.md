# OnlyMentors.ai - Updated Workflow Diagrams (Complete Platform)

## 1. Overall System Architecture

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend (React)"
        UI[User Interface]
        Auth[Authentication Components]
        Profile[User Profile]
        Mentor[Mentor Selection]
        Question[Question Interface]
        Admin[Admin Dashboard]
    end

    %% Backend Layer
    subgraph "Backend (FastAPI)"
        API[REST API Server]
        AuthAPI[Auth Endpoints]
        UserAPI[User Endpoints]
        MentorAPI[Mentor Endpoints]
        AdminAPI[Admin Endpoints]
    end

    %% Database Layer
    subgraph "Database (MongoDB)"
        UserDB[(Users Collection)]
        MentorDB[(Mentors Collection)]
        QuestionDB[(Questions Collection)]
        InteractionDB[(Interactions Collection)]
        AdminDB[(Admin Collection)]
    end

    %% External Services
    subgraph "External Services"
        GoogleOAuth[Google OAuth - WORKING]
        FacebookOAuth[Facebook OAuth - WORKING]
        OpenAI[OpenAI API]
        TwilioSMS[Twilio SMS & 2FA]
        SMTP2GO[SMTP2GO Email Service]
        Stripe[Stripe Payments - $9.99/month]
    end

    %% Connections
    UI --> API
    Auth --> AuthAPI
    Profile --> UserAPI
    Mentor --> MentorAPI
    Question --> MentorAPI
    Admin --> AdminAPI

    AuthAPI --> UserDB
    UserAPI --> UserDB
    MentorAPI --> MentorDB
    MentorAPI --> QuestionDB
    MentorAPI --> InteractionDB
    AdminAPI --> UserDB
    AdminAPI --> AdminDB

    AuthAPI --> GoogleOAuth
    AuthAPI --> FacebookOAuth
    MentorAPI --> OpenAI
    AdminAPI --> SMTP2GO
    AdminAPI --> TwilioSMS
    UserAPI --> Stripe
    UserAPI --> TwilioSMS
```

## 2. User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant O as OAuth Provider

    %% Registration Flow
    U->>F: Access signup page
    F->>U: Show comprehensive signup form
    U->>F: Fill profile data (name, email, phone, preferences)
    F->>B: POST /api/auth/register
    B->>DB: Create user with complete profile
    B->>F: Return JWT token + user data
    F->>U: Redirect to categories page

    %% OAuth Flow
    U->>F: Click OAuth button (Google/Facebook)
    F->>O: Redirect to OAuth provider
    O->>U: Show OAuth consent
    U->>O: Approve permissions
    O->>F: Return OAuth code
    F->>B: POST /api/auth/google or /api/auth/facebook
    B->>O: Validate OAuth token
    O->>B: Return user info
    B->>DB: Create/update user
    B->>F: Return JWT token + user data
    F->>U: Login successful, redirect to app

    %% Login Flow
    U->>F: Enter email/password
    F->>B: POST /api/auth/login
    B->>DB: Validate credentials
    DB->>B: Return user data
    B->>F: Return JWT token + user data
    F->>U: Login successful
```

## 3. User Journey Flow

```mermaid
flowchart TD
    Start([User Visits Site]) --> Auth{Authenticated?}
    
    Auth -->|No| Login[Login/Signup Page]
    Auth -->|Yes| Categories[Categories Page]
    
    Login --> OAuth[OAuth Buttons]
    Login --> EmailAuth[Email/Password Form]
    Login --> CompSignup[Comprehensive Signup]
    
    OAuth --> GoogleAuth[Google OAuth]
    OAuth --> FacebookAuth[Facebook OAuth]
    
    EmailAuth --> ValidateAuth{Valid Credentials?}
    ValidateAuth -->|No| AuthError[Show Error]
    ValidateAuth -->|Yes| Categories
    
    CompSignup --> Step1[Step 1: Personal Info]
    Step1 --> Step2[Step 2: Subscription Plan]
    Step2 --> Step3[Step 3: Payment/Review]
    Step3 --> CreateAccount[Create Account]
    CreateAccount --> Categories
    
    Categories --> SelectCategory[Select Category]
    SelectCategory --> MentorGrid[Mentor Grid]
    MentorGrid --> SelectMentors[Select Mentors (Max 5)]
    SelectMentors --> QuestionForm[Question Form]
    QuestionForm --> SubmitQuestion[Submit Question]
    
    SubmitQuestion --> CheckSubscription{Subscribed?}
    CheckSubscription -->|No| CheckLimit{Questions Left?}
    CheckLimit -->|No| Subscription[Subscription Page]
    CheckLimit -->|Yes| ProcessQuestion[Process Question]
    CheckSubscription -->|Yes| ProcessQuestion
    
    ProcessQuestion --> AIResponse[Get AI Responses]
    AIResponse --> ShowResponses[Show Responses]
    ShowResponses --> NextAction{User Choice}
    
    NextAction --> AskAgain[Ask Another Question]
    NextAction --> DiffMentors[Select Different Mentors]
    NextAction --> History[View History]
    NextAction --> Profile[User Profile]
    
    Categories --> Profile
    Profile --> EditProfile[Edit Profile Information]
    Profile --> ChangePassword[Change Password]
    Profile --> CommPrefs[Communication Preferences]
    
    AuthError --> Login
    AskAgain --> QuestionForm
    DiffMentors --> MentorGrid
    Subscription --> Payment[Stripe Checkout]
    Payment --> Categories
```

## 4. Admin Workflow

```mermaid
flowchart TD
    AdminStart([Admin Access]) --> AdminLogin[Admin Login]
    AdminLogin --> ValidateAdmin{Valid Admin?}
    ValidateAdmin -->|No| AdminError[Access Denied]
    ValidateAdmin -->|Yes| AdminDash[Admin Dashboard]
    
    AdminDash --> UserMgmt[User Management]
    AdminDash --> MentorMgmt[Mentor Management]
    AdminDash --> ContentMod[Content Moderation]
    AdminDash --> Reports[Reports & Analytics]
    AdminDash --> Payouts[Payout Management]
    AdminDash --> AIAgents[AI Agent Framework]
    
    UserMgmt --> UserList[View All Users]
    UserList --> UserActions{Select Action}
    
    UserActions --> ResetPwd[Reset Password]
    UserActions --> SuspendUser[Suspend User]
    UserActions --> DeleteUser[Delete User]
    UserActions --> UnsuspendUser[Unsuspend User]
    
    ResetPwd --> ResetModal[Reset Password Modal]
    ResetModal --> SendEmail[Send Reset Email]
    SendEmail --> EmailSent[Email Notification Sent]
    
    SuspendUser --> SuspendModal[Suspend Modal]
    SuspendModal --> SelectReason[Select Suspension Reason]
    SelectReason --> ConfirmSuspend[Confirm Suspension]
    ConfirmSuspend --> SuspendEmail[Send Suspension Email]
    SuspendEmail --> UserSuspended[User Suspended]
    
    DeleteUser --> DeleteModal[Delete Modal]
    DeleteModal --> ConfirmDelete[Confirm Permanent Deletion]
    ConfirmDelete --> DeleteEmail[Send Deletion Email]
    DeleteEmail --> UserDeleted[User Deleted]
    
    UnsuspendUser --> UnsuspendModal[Unsuspend Modal]
    UnsuspendModal --> UnsuspendReason[Enter Unsuspend Reason]
    UnsuspendReason --> RestoreAccess[Restore User Access]
    
    MentorMgmt --> CreateMentor[Create New Mentors]
    MentorMgmt --> EditMentor[Edit Mentor Profiles]
    MentorMgmt --> MentorStatus[Manage Mentor Status]
    
    AdminError --> AdminLogin
```

## 5. Data Flow & Relationships

```mermaid
erDiagram
    Users {
        string user_id PK
        string email
        string password_hash
        string full_name
        string phone_number
        object communication_preferences
        string subscription_plan
        boolean is_subscribed
        datetime subscription_expires
        int questions_asked
        array question_history
        array mentor_interactions
        boolean profile_completed
        boolean is_active
        datetime created_at
        datetime last_login
    }
    
    Mentors {
        string id PK
        string name
        string title
        string category
        string bio
        string expertise
        string image_url
        boolean is_active
        datetime created_at
    }
    
    Questions {
        string question_id PK
        string user_id FK
        string category
        string question
        array mentor_ids
        array responses
        datetime created_at
        string status
    }
    
    MentorInteractions {
        string interaction_id PK
        string user_id FK
        string mentor_id FK
        string question_id FK
        string question
        string response
        datetime timestamp
    }
    
    Admins {
        string admin_id PK
        string email
        string password_hash
        string full_name
        string role
        datetime created_at
        datetime last_login
    }
    
    AuditLogs {
        string log_id PK
        string admin_id FK
        string action
        string target_user_id
        object details
        datetime timestamp
    }
    
    Users ||--o{ Questions : "asks"
    Users ||--o{ MentorInteractions : "has"
    Mentors ||--o{ MentorInteractions : "responds"
    Questions ||--o{ MentorInteractions : "generates"
    Admins ||--o{ AuditLogs : "creates"
```

## 6. Component Architecture

```mermaid
graph TB
    subgraph "App.js (Main Router)"
        MainApp[MainApp Component]
        AdminApp[AdminApp Component]
        CreatorApp[CreatorApp Component]
    end
    
    subgraph "Authentication Components"
        UserSignup[UserSignup - 3 Step Process]
        GoogleOAuth[GoogleOAuthButton]
        FacebookOAuth[FacebookOAuthButton]
        ForgotPassword[ForgotPasswordForm]
        ResetPassword[ResetPasswordForm]
    end
    
    subgraph "User Components"
        UserProfile[UserProfile - Personal Info & Password]
        Categories[Categories Grid]
        MentorGrid[Mentor Selection Grid]
        QuestionForm[Question Interface]
        ResponseView[Response Display]
        History[Question History]
        Subscription[Subscription Plans]
    end
    
    subgraph "Admin Components"
        AdminLogin[AdminLogin]
        AdminDashboard[AdminDashboardSimple]
        UserManagement[UserManagement]
    end
    
    subgraph "Creator Components"
        CreatorLogin[CreatorLogin]
        CreatorSignup[CreatorSignup]
        CreatorDashboard[CreatorDashboard]
        CreatorVerification[CreatorVerification]
        ContentUpload[ContentUpload]
    end
    
    subgraph "UI Components"
        Button[Button]
        Card[Card]
        Input[Input]
        Tabs[Tabs]
        Dialog[Dialog]
        Avatar[Avatar]
    end
    
    MainApp --> UserSignup
    MainApp --> UserProfile
    MainApp --> Categories
    MainApp --> MentorGrid
    MainApp --> QuestionForm
    MainApp --> ResponseView
    MainApp --> History
    MainApp --> Subscription
    
    AdminApp --> AdminLogin
    AdminApp --> AdminDashboard
    AdminDashboard --> UserManagement
    
    CreatorApp --> CreatorLogin
    CreatorApp --> CreatorSignup
    CreatorApp --> CreatorDashboard
```

## 7. API Endpoint Map

```mermaid
mindmap
  root((OnlyMentors.ai API))
    Authentication
      POST /api/auth/register
      POST /api/auth/login
      POST /api/auth/google
      POST /api/auth/facebook
      GET /api/auth/me
      POST /api/forgot-password/request
      POST /api/forgot-password/reset
    
    User Management
      GET /api/user/profile
      PUT /api/user/profile
      GET /api/user/profile/complete
      PUT /api/user/profile/communication-preferences
      GET /api/user/question-history
      PUT /api/user/password
    
    Mentors & Questions
      GET /api/categories
      POST /api/questions/ask
      GET /api/questions/history
      POST /api/mentor/{mentor_id}/ask
    
    Admin Endpoints
      POST /api/admin/login
      GET /api/admin/users
      PUT /api/admin/users/{user_id}/suspend
      PUT /api/admin/users/{user_id}/reset-password
      DELETE /api/admin/users/{user_id}
      GET /api/admin/audit-logs
    
    Payments
      POST /api/payments/checkout
      GET /api/payments/status/{session_id}
```