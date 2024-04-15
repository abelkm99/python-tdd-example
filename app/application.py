from datetime import date
import msgspec


class OrderLine(msgspec.Struct, frozen=True):
    order_ref: str
    SKU: str
    qty: int

    def __hash__(self):
        return hash(self.order_ref)

    def __eq__(self, other):
        return self.order_ref == other.order_ref


class Batch(msgspec.Struct):
    ref: str
    SKU: str
    qty: int
    eta: date | None = None

    _allocated: set[OrderLine] = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self.qty -= line.qty
            self._allocated.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocated:
            self.qty += line.qty
            self._allocated.remove(line)

    @property
    def available_quantity(self) -> int:
        return self.qty

    def can_allocate(self, line: OrderLine) -> bool:
        return self.SKU == line.SKU and self.qty >= line.qty
