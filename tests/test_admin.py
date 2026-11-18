"""ПР10: реальные запросы Django Admin и проверка ограничений доступа."""
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from registrations.models import Registration


@pytest.fixture
def registration(orm_database):
    return Registration.objects.create(event_id=1, participant_id=1, registration_date=date(2026, 10, 1))


@pytest.fixture
def superuser(orm_database):
    # Пароль нужен только временной тестовой БД; force_login не требует его публикации.
    return get_user_model().objects.create_superuser(username="test-admin", email="admin@example.invalid", password=None)


def test_admin_requires_staff(client, orm_database):
    response = client.get(reverse("admin:index"))
    assert response.status_code == 302 and "/admin/login/" in response.url
    user = get_user_model().objects.create_user(username="visitor", password=None)
    client.force_login(user)
    assert client.get(reverse("admin:index")).status_code == 302


@pytest.mark.parametrize("model", ["organizations_organization", "events_event", "participants_participant", "registrations_registration"])
def test_registered_model_lists(client, superuser, model):
    client.force_login(superuser)
    response = client.get(reverse(f"admin:{model}_changelist"))
    assert response.status_code == 200
    assert response.context["cl"].model_admin.list_per_page == 20


def test_admin_registration_search_filter_and_action(client, superuser, registration):
    client.force_login(superuser)
    url = reverse("admin:registrations_registration_changelist")
    assert client.get(url, {"q": "Иванов"}).context["cl"].result_count == 1
    assert client.get(url, {"q": "Несуществующее имя"}).context["cl"].result_count == 0
    assert client.get(url, {"status__exact": "CANCELLED"}).context["cl"].result_count == 0
    response = client.post(url, {"action": "cancel_selected", "_selected_action": [registration.pk]})
    assert response.status_code == 302
    registration.refresh_from_db()
    assert registration.status == Registration.Status.CANCELLED
    assert client.get(url, {"status__exact": "CANCELLED"}).context["cl"].result_count == 1


def test_admin_related_inlines(client, superuser, registration):
    client.force_login(superuser)
    for name, pk in [("events_event", registration.event_id), ("participants_participant", registration.participant_id)]:
        response = client.get(reverse(f"admin:{name}_change", args=[pk]))
        assert response.status_code == 200
        inlines = response.context["inline_admin_formsets"]
        assert len(inlines) == 1 and inlines[0].formset.queryset.get().pk == registration.pk


def test_staff_with_view_permission_cannot_change(client, orm_database, registration):
    user = get_user_model().objects.create_user(username="viewer", is_staff=True, password=None)
    user.user_permissions.add(Permission.objects.get(codename="view_registration"))
    client.force_login(user)
    response = client.get(reverse("admin:registrations_registration_changelist"))
    assert response.status_code == 200
    assert "cancel_selected" not in response.context["cl"].model_admin.get_actions(response.wsgi_request)
    change = reverse("admin:registrations_registration_change", args=[registration.pk])
    assert client.post(change, {"status": "CANCELLED"}).status_code == 403


def test_admin_crud_organization(client, superuser):
    from organizations.models import Organization

    client.force_login(superuser)
    add_url = reverse("admin:organizations_organization_add")
    data = {"name": "Проверка админки", "city": "Казань", "address": "Учебный адрес", "phone": "123", "email": ""}
    assert client.post(add_url, data).status_code == 302
    item = Organization.objects.get(name=data["name"])
    change_url = reverse("admin:organizations_organization_change", args=[item.pk])
    assert client.post(change_url, {**data, "name": "Обновлено"}).status_code == 302
    item.refresh_from_db()
    assert item.name == "Обновлено"
    delete_url = reverse("admin:organizations_organization_delete", args=[item.pk])
    assert client.post(delete_url, {"post": "yes"}).status_code == 302
    assert not Organization.objects.filter(pk=item.pk).exists()


def test_admin_blocks_duplicate_registration(client, superuser, registration):
    client.force_login(superuser)
    response = client.post(reverse("admin:registrations_registration_add"), {
        "event": registration.event_id, "participant": registration.participant_id,
        "registration_date": "2026-10-02", "status": "CONFIRMED", "notes": "",
    })
    assert response.status_code == 200 and response.context["adminform"].form.errors
    assert Registration.objects.count() == 1
