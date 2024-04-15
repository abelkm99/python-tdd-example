# from ..app.application import Batch, OrderLine
# from datetime import date, timedelta
# import pytest


# def test_1():
#     assert 1 == 1


# today = date.today()
# tomorrow = today + timedelta(days=1)
# later = tomorrow + timedelta(days=10)


# @pytest.fixture(scope="function")
# def batch() -> Batch:
#     return Batch(ref="batch-001", SKU="SMALL-TABLE", qty=20)


# def test_allocating_to_a_batch_reduces_the_available_quantity(batch: Batch):
#     line = OrderLine(order_ref="order-ref", SKU="SMALL-TABLE", qty=2)
#     batch.allocate(line)
#     assert batch.available_quantity == 18


# def test_can_allocate_if_available_greater_than_required(batch: Batch):
#     line1 = OrderLine(order_ref="order-ref", SKU="SMALL-TABLE", qty=2)
#     assert batch.can_allocate(line1)


# def test_cannot_allocate_if_available_smaller_than_required(batch: Batch):
#     line = OrderLine(order_ref="order-ref", SKU="SMALL-TABLE", qty=22)
#     assert not batch.can_allocate(line)


# def test_can_allocate_if_available_equal_to_required(batch: Batch):
#     line = OrderLine(order_ref="order-ref", SKU="SMALL-TABLE", qty=20)
#     assert batch.can_allocate(line)


# # def test_prefers_warehouse_batches_to_shipments():
# #     pytest.fail("todo")


# # def test_prefers_earlier_batches():
# #     pytest.fail("todo")
