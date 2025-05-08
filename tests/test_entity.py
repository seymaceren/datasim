from pytest import raises
from datasim import Entity, State, World


class IdleState(State):
    def __init__(self, name, entity):
        super().__init__(name, entity)

    def tick(self):
        return super().tick()


def test_entity():
    World.reset()
    world = World()
    en1 = Entity("Test entity 1", IdleState)
    world.add(en1)
    en2 = Entity("Test entity 2", IdleState("Idle2", None))
    world.add(en2)
    assert en2.state.name == "Idle2"
    with raises(TypeError, match=".*not a subclass of State.*"):
        en2.state = world
    old_state = en2.state
    en2.state = IdleState
    assert world.simulate(tpu=1.0, end_tick=20)
    assert len(world.entities) == 2
    assert world.entity(en1.name).id == en1.id
    assert world.entity("Test entity 2") == en2
    assert en2.state != old_state
    with raises(ValueError, match=".*already belongs to.*"):
        en1.state = old_state
    world.wait()
