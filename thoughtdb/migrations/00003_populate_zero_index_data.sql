insert into organization(id, name) values (0, 'None');
insert into collection(id, name, organization_id) values (0, 'None', 0);
insert into document_type(id, name) values (0, 'None');
insert into document_type(id, name) values (1, 'Text');
insert into document_type(id, name) values (1, 'PDF');
insert into document_type(id, name) values (1, 'Word');
insert into document_type(id, name) values (1, 'Excel');
insert into document(id, name, collection_id, organization_id, document_type_id)
values (0, 'None', 0, 0, 0)