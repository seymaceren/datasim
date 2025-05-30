from pytest import raises
from datasim import Entity, Runner, State, World


class IdleState(State):
    def __init__(self, name, entity):
        super().__init__(name, entity)

    def tick(self):
        return super().tick()


def test_entity():
    world = Runner(World).worlds[0]
    en1 = Entity(world, "Test entity 1", IdleState)
    world.add(en1)
    en2 = Entity(world, "Test entity 2", IdleState("Idle2", None))
    world.add(en2)
    assert en2.state.name == "Idle2"
    with raises(TypeError, match=".*not a subclass of State.*"):
        en2.state = world
    old_state = en2.state
    en2.state = IdleState
    assert world._simulate(tpu=1.0, end_tick=20)
    assert len(world.entities) == 2
    assert world.entity(en1.id) == en1
    assert world.entity("Test entity 2") == en2
    assert en2.state != old_state
    with raises(ValueError, match=".*already belongs to.*"):
        en1.state = old_state
    world._wait()
