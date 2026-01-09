erDiagram

%% Project: example

%% Enum: answer
%%   - n/a
%%   - yes
%%   - no

"another.user" {
    int id PK
    varchar name UK
    decimal value
}

"example.option" {
    int id PK
    int seq UK
    varchar content UK
}

"example.question" {
    int id PK
    varchar content
    int option_id FK
}

"example.questionare" {
    int id PK
    varchar name
    int question_id FK
}

"example.user_survey" {
    int id
    int user_id PK,FK
    int questionare_id PK,FK
    timestamp submission_date
    answer answer_given
}

"example.user_survey" }o--|| "another.user" : "user_id - id"

"example.questionare" }o--|| "example.question" : "question_id - id"

"example.question" }o--|| "example.option" : "option_id - id"

"example.user_survey" }o--|| "example.questionare" : "questionare_id - id"

