create table organization
(
    id           integer not null,
    name         varchar(255) default 'default' not null unique,
    auth_key     varchar(255) default '' not null unique,
    date_created timestamp    default CURRENT_TIMESTAMP,
    primary key (id)
);

create table collection
(
    id              integer                not null,
    name            varchar(255) default 'default' not null,
    date_created    timestamp    default CURRENT_TIMESTAMP,
    organization_id integer      default 0 not null references organization (id) on update cascade on delete cascade,
    primary key (id),
    unique (name, organization_id)
);

create table conversation_session
(
    id              integer                not null,
    name            varchar(255) default 'default',
    date_created    timestamp    default CURRENT_TIMESTAMP,
    organization_id integer      default 0 not null references organization (id) on update cascade on delete cascade,
    collection_id   integer      default 0 not null references collection (id) on update cascade on delete cascade,
    primary key (id)
);

create table conversation
(
    id                      integer                not null,
    name                    varchar(255) default 'default',
    date_created            timestamp    default CURRENT_TIMESTAMP,
    organization_id         integer      default 0 not null references organization (id) on update cascade on delete cascade,
    collection_id           integer      default 0 not null references collection (id) on update cascade on delete cascade,
    conversation_session_id integer      default 0 not null references conversation_session (id) on update cascade on delete cascade,
    primary key (id)
);

create table conversation_metadata
(
    id              integer                not null,
    key_name        varchar(255) default 'default',
    key_value       blob,
    date_created    timestamp    default CURRENT_TIMESTAMP,
    conversation_id integer      default 0 not null references conversation (id) on update cascade on delete cascade,
    primary key (id)
);

create table conversation_summary
(
    id              integer                not null,
    name            varchar(255) default 'default',
    person          varchar(255) default 'group',
    data            blob,
    meta            blob,
    date_created    timestamp    default CURRENT_TIMESTAMP,
    conversation_id integer      default 0 not null references conversation (id) on update cascade on delete cascade,
    primary key (id)
);

create table conversation_history
(
    id                      integer                not null,
    name                    varchar(255) default 'default',
    person_from             varchar(255) default 'group',
    person_to               varchar(255) default 'group',
    data                    blob,
    meta                    blob,
    date_created            timestamp    default CURRENT_TIMESTAMP,
    conversation_id         integer      default 0 not null references conversation (id) on update cascade on delete cascade,
    conversation_summary_id integer      default 0 not null references conversation_summary (id) on update cascade on delete cascade,
    primary key (id)
);


create table document_type
(
    id           integer not null,
    name         varchar(255) default 'default',
    date_created timestamp    default CURRENT_TIMESTAMP,
    primary key (id)
);

create table document
(
    id               integer                not null,
    name             varchar(255) default 'default',
    data             blob,
    meta             blob,
    date_created     timestamp    default CURRENT_TIMESTAMP,
    document_type_id integer      default 0 not null references document_type (id) on update cascade on delete cascade,
    organization_id  integer      default 0 not null references organization (id) on update cascade on delete cascade,
    collection_id    integer      default 0 not null references collection (id) on update cascade on delete cascade,
    primary key (id)
);

create table document_metadata
(
    id           integer                not null,
    key_name     varchar(255) default 'default',
    key_value    blob,
    date_created timestamp    default CURRENT_TIMESTAMP,
    document_id  integer      default 0 not null references document (id) on update cascade on delete cascade,
    primary key (id)
);

create table document_chapter
(
    id           integer                not null,
    name         varchar(255) default 'default',
    data         blob,
    meta         blob,
    date_created timestamp    default CURRENT_TIMESTAMP,
    document_id  integer      default 0 not null references document (id) on update cascade on delete cascade,
    primary key (id)
);

create table document_paragraph
(
    id                  integer                not null,
    name                varchar(255) default 'default',
    data                blob,
    meta                blob,
    date_created        timestamp    default CURRENT_TIMESTAMP,
    document_chapter_id integer      default 0 not null references document_chapter (id) on update cascade on delete cascade,
    document_id         integer      default 0 not null references document (id) on update cascade on delete cascade,
    primary key (id)
);

create table document_sentence
(
    id                    integer                not null,
    name                  varchar(255) default 'default',
    data                  blob,
    meta                  blob,
    date_created          timestamp    default CURRENT_TIMESTAMP,
    document_paragraph_id integer      default 0 not null references document_paragraph (id) on update cascade on delete cascade,
    document_chapter_id   integer      default 0 not null references document_chapter (id) on update cascade on delete cascade,
    document_id           integer      default 0 not null references document (id) on update cascade on delete cascade,
    primary key (id)
);

create table document_word
(
    id                    integer                not null,
    name                  varchar(255) default 'default',
    data                  blob,
    meta                  blob,
    date_created          timestamp    default CURRENT_TIMESTAMP,
    document_sentence_id  integer      default 0 not null references document_sentence (id) on update cascade on delete cascade,
    document_paragraph_id integer      default 0 not null references document_paragraph (id) on update cascade on delete cascade,
    document_chapter_id   integer      default 0 not null references document_chapter (id) on update cascade on delete cascade,
    document_id           integer      default 0 not null references document (id) on update cascade on delete cascade,
    primary key (id)
);

create table image
(
    id              integer             not null,
    data            blob,
    date_created    timestamp default CURRENT_TIMESTAMP,
    document_id     integer   default 0 not null references document (id) on update cascade on delete cascade,
    conversation_id integer   default 0 not null references conversation (id) on update cascade on delete cascade,
    organization_id integer   default 0 not null references organization (id) on update cascade on delete cascade,
    collection_id   integer   default 0 not null references collection (id) on update cascade on delete cascade,
    primary key (id)
);

create table embedding
(
    id                      integer                not null,
    data                    blob,
    date_created            timestamp    default CURRENT_TIMESTAMP,
    model_name              varchar(255) default 'default',
    column_name             varchar(255) default '',
    table_name              varchar(255) default '',
    key_name                varchar(255) default 'id',
    key_value               varchar(255) default '',
    primary key (id)
);


