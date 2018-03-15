# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-15 17:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0089_auto_20180315_1114'),
    ]

    operations = [
        migrations.RunSQL(
            [
                """
                -- Create collection groups - Read/Write/Admin
                INSERT INTO auth_group (id, name)
                    SELECT nextval('auth_group_id_seq'), 'collections_' || C.id || '_read'
                    FROM osf_collection C;
                INSERT INTO auth_group (id, name)
                    SELECT nextval('auth_group_id_seq'), 'collections_' || C.id || '_write'
                    FROM osf_collection C;
                INSERT INTO auth_group (id, name)
                    SELECT nextval('auth_group_id_seq'), 'collections_' || C.id || '_admin'
                    FROM osf_collection C;
                """, """
                -- Grant collection groups perms
                -- -- Because the collection id is encoded in the group name, we can use split_part to extract it
                -- ---- and avoid doing an extra join on osf_collection
                -- Read granted to R/W/A groups
                INSERT INTO osf_collectiongroupobjectpermission (id, content_object_id, group_id, permission_id)
                    SELECT nextval('osf_collectiongroupobjectpermission_id_seq'), split_part(G.name, '_', 2) :: INT, G.id :: INT, P.id
                    FROM auth_group G
                    LEFT JOIN LATERAL (
                        SELECT id
                        FROM auth_permission
                        WHERE codename = 'read_collection'
                    ) P ON TRUE
                    WHERE G.name LIKE 'collections_%';
                -- Write granted to W/A groups
                INSERT INTO osf_collectiongroupobjectpermission (id, content_object_id, group_id, permission_id)
                    SELECT nextval('osf_collectiongroupobjectpermission_id_seq'), split_part(G.name, '_', 2) :: INT, G.id :: INT, P.id
                    FROM auth_group G
                    LEFT JOIN LATERAL (
                        SELECT id
                        FROM auth_permission
                        WHERE codename = 'write_collection'
                    ) P ON TRUE
                    WHERE G.name LIKE 'collections_%_write'
                        OR G.name LIKE 'collections_%_admin';
                -- Admin granted to A groups
                INSERT INTO osf_collectiongroupobjectpermission (id, content_object_id, group_id, permission_id)
                    SELECT nextval('osf_collectiongroupobjectpermission_id_seq'), split_part(G.name, '_', 2) :: INT, G.id :: INT, P.id
                    FROM auth_group G
                    LEFT JOIN LATERAL (
                        SELECT id
                        FROM auth_permission
                        WHERE codename = 'admin_collection'
                    ) P ON TRUE
                    WHERE G.name LIKE 'collections_%_admin';
                """, """
                -- Add collection creators to their respective admin groups
                INSERT INTO osf_osfuser_groups (id, osfuser_id, group_id)
                    SELECT nextval('osf_osfuser_groups_id_seq'), C.creator_id, G.id
                    FROM osf_collection C
                    LEFT JOIN LATERAL (
                        SELECT id
                        FROM auth_group
                        WHERE name = 'collections_' || C.id || '_admin'
                    ) G ON TRUE;
                """
            ], [
                """
                -- Delete things from the forward
                DELETE FROM osf_osfuser_groups
                    WHERE group_id IN (SELECT id
                                       FROM auth_group
                                       WHERE name LIKE 'collections_%');
                DELETE FROM osf_collectiongroupobjectpermission;
                DELETE FROM auth_group
                    WHERE name LIKE 'collections_%';
                """, """
                -- Reset id sequence values
                SELECT setval('osf_osfuser_groups_id_seq', max(id) + 1)
                    FROM osf_osfuser_groups;
                SELECT setval('osf_collectiongroupobjectpermission_id_seq', 1);
                SELECT setval('auth_group_id_seq', max(id) + 1)
                    FROM auth_group;
                """
            ]
        )
    ]
