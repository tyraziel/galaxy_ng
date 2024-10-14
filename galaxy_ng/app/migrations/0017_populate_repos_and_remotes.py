# Generated by Django 2.2.19 on 2021-03-24 22:07

from django.db import migrations

REPOSITORIES = [
    {
        "name": "published",
        "description": "Certified content repository",
        "pulp_type": "ansible.ansible",
        "next_version": 1,
    },
    {
        "name": "community",
        "description": "Community content repository",
        "pulp_type": "ansible.ansible",
        "next_version": 1,
        "remote": {
            "name": "community",
            "url": "https://galaxy.ansible.com/api/",
            "requirements_file": None,
            "token": None,
            "auth_url": None,
            "pulp_type": "ansible.ansible",
            "rate_limit": 8,
        }
    },
    {
        "name": "rh-certified",
        "description": "Red Hat certified content repository",
        "pulp_type": "ansible.ansible",
        "next_version": 1,
        "remote": {
            "name": "rh-certified",
            "url": "https://console.redhat.com/api/automation-hub/content/published/",
            "requirements_file": None,
            "token": None,
            "auth_url": (
                "https://sso.redhat.com/auth/realms/"
                "redhat-external/protocol/openid-connect/token"
            ),
            "pulp_type": "ansible.ansible",
            "rate_limit": 8,
        }
    }
]
# NOTE:`staging` & `rejected` are created by 0010_add_staging_rejected_repos.py


def populate_initial_repos(apps, schema_editor):
    """Populates initial data for Automation Hub.

    - Staging and rejected repos are covered by migration 0010
    - Remotes are created only if doesn't exist and is specified in REMOTES dict
      matching the same name as repository.
    - Repositories are created using REPOSITORIES data and only if doesn't exist.
    - Distributions are created only if not found with same name as repository.
    - Reverse us NOOP so nothing is done if transaction fails to avoid corrupting
      existing data.

    """

    db_alias = schema_editor.connection.alias

    AnsibleRepository = apps.get_model('ansible', 'AnsibleRepository')
    AnsibleDistribution = apps.get_model('ansible', 'AnsibleDistribution')
    CollectionRemote = apps.get_model('ansible', 'CollectionRemote')
    RepositoryVersion = apps.get_model('core', 'RepositoryVersion')

    for repo_data in REPOSITORIES:

        remote = repo_data.pop("remote", None)
        if remote is not None:
            remote, _ = CollectionRemote.objects.using(db_alias).get_or_create(
                name=remote["name"], defaults=remote
            )
        repo_data["remote"] = remote

        repository, _ = AnsibleRepository.objects.using(db_alias).get_or_create(
            name=repo_data["name"],
            defaults=repo_data
        )

        if not RepositoryVersion.objects.filter(repository__name=repository.name):
            RepositoryVersion.objects.using(db_alias).create(
                repository=repository,
                number=0,
                complete=True
            )

        AnsibleDistribution.objects.using(db_alias).get_or_create(
            base_path=repository.name,
            defaults={
                "name": repository.name,
                "base_path": repository.name,
                "remote": remote,
                "repository": repository,
                "pulp_type": "ansible.ansible"
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0016_containerregistryremote_containerregistryrepos_containersynctask'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_initial_repos,
            reverse_code=migrations.RunPython.noop
        )
    ]
