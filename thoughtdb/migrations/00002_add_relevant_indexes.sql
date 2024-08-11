create unique index if not exists idx_organization_name on organization(name);
create unique index if not exists idx_collection_name on collection(name);
create unique index if not exists idx_document_name on  document(name);
create unique index if not exists idx_conversation_name_session on conversation(name, conversation_session_id);
create index if not exists idx_conversation_metadata on conversation_metadata(key_name);
create index if not exists idx_document_metadata on document_metadata(key_name);