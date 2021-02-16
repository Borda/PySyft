# third party
import pytest
import torch as th

# syft absolute
import syft as sy


@pytest.mark.parametrize("with_verify_key", [True, False])
def test_make_searchable(with_verify_key: bool) -> None:
    bob = sy.VirtualMachine(name="Bob")
    root_client = bob.get_root_client()
    client = bob.get_client()

    ten = th.tensor([1, 2])
    ptr = ten.send(root_client)

    assert len(client.store) == 0

    if with_verify_key:
        ptr.update_searchability(target_verify_key=client.verify_key)
    else:
        ptr.update_searchability()

    assert len(client.store) == 1


@pytest.mark.parametrize("with_verify_key", [True, False])
def test_make_unsearchable(with_verify_key: bool) -> None:
    bob = sy.VirtualMachine(name="Bob")
    root_client = bob.get_root_client()
    client = bob.get_client()

    ten = th.tensor([1, 2])
    ptr = ten.send(root_client)

    if with_verify_key:
        ptr.update_searchability(target_verify_key=client.verify_key)
    else:
        ptr.update_searchability()

    assert len(client.store) == 1

    if with_verify_key:
        ptr.update_searchability(searchable=False, target_verify_key=client.verify_key)
    else:
        ptr.update_searchability(searchable=False)

    assert len(client.store) == 0


def test_searchable_property() -> None:
    bob = sy.VirtualMachine(name="Bob")
    root_client = bob.get_root_client()
    client = bob.get_client()

    ten = th.tensor([1, 2])
    ptr = ten.send(root_client)
    assert len(client.store) == 0

    ptr.searchable = False
    assert len(client.store) == 0

    ptr.searchable = True
    assert len(client.store) == 1

    ptr.searchable = True
    assert len(client.store) == 1

    ptr.searchable = False
    assert len(client.store) == 0


@pytest.mark.xfail
def test_tags() -> None:
    bob = sy.VirtualMachine(name="Bob")
    client = bob.get_client()
    root_client = bob.get_root_client()

    ten = th.tensor([1, 2])

    ten = ten.tag("tag1", "tag1", "other")
    assert ten.tags == ["tag1", "other"]

    # .send without `tags` passed in
    ptr = ten.send(root_client)
    assert ptr.tags == ["tag1", "other"]

    # .send with `tags` passed in
    ptr = ten.send(root_client, tags=["tag2", "tag2", "other"])
    assert ten.tags == ["tag2", "other"]
    assert ptr.tags == ["tag2", "other"]

    th.Tensor([1, 2, 3]).send(root_client, searchable=True, tags=["a"])
    th.Tensor([1, 2, 3]).send(root_client, searchable=True, tags=["b"])
    th.Tensor([1, 2, 3]).send(root_client, searchable=True, tags=["c"])
    th.Tensor([1, 2, 3]).send(root_client, searchable=True, tags=["d"])
    sy.lib.python.Int(2).send(root_client, searchable=True, tags=["e"])
    sy.lib.python.List([1, 2, 3]).send(root_client, searchable=True, tags=["f"])

    a = root_client.store["a"]
    b = root_client.store["b"]
    c = root_client.store["c"]
    d = root_client.store["d"]
    e = root_client.store["e"]

    result_ptr = a.requires_grad
    assert result_ptr.tags == ["a", "requires_grad"]

    result_ptr = b.pow(e)
    assert result_ptr.tags == ["b", "e", "pow"]

    result_ptr = c.pow(exponent=e)
    assert result_ptr.tags == ["c", "e", "pow"]

    result_ptr = root_client.torch.pow(d, e)
    assert result_ptr.tags == ["d", "e", "pow"]

    result_ptr = root_client.torch.pow(d, 3)
    assert result_ptr.tags == ["d", "pow"]

    # __len__ auto gets if you have permission
    f_root = root_client.store["f"]

    assert len(f_root) == 3

    # TODO: Fix this test
    f_guest = client.store["f"]
    result_ptr = f_guest.__len__()
    assert result_ptr is not None  # should be a pointer?
    assert result_ptr.tags == ["f", "__len__"]


def test_description() -> None:
    bob = sy.VirtualMachine(name="Bob")
    root_client = bob.get_root_client()

    ten = th.tensor([1, 2])

    ten = ten.describe("description 1")
    assert ten.description == "description 1"

    # .send without `description` passed in
    ptr = ten.send(root_client)
    assert ptr.description == "description 1"

    # .send with `description` passed in
    ptr = ten.send(root_client, description="description 2")
    assert ten.description == "description 2"
    assert ptr.description == "description 2"