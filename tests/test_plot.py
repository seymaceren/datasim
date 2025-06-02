from datasim import (
    Entity,
    Queue,
    Resource,
    Runner,
    World,
    XYData,
)


def test_plot():
    world = Runner(World).worlds[0]
    print(world.title)
    xydata = XYData(world)
    xydata.append(10.0, 20.0)
    xydata.append(20.0, 50.0)
    xydata.append(30.0, 30.0)
    assert xydata._buffer_index == 3
    plot = world.add_data("plot1", xydata)

    water = Resource(world, "water", "water", 0, 0.0, 0, 1000.0, 100.0)
    assert water._amount == 100.0

    teller = Queue(world, "teller", 5)
    assert teller.capacity == 5
    assert len(teller) == 0
    teller.enqueue(Entity(world), 10.0)
    teller.enqueue(Entity(world), 9.0)
    teller.enqueue(Entity(world), 8.0)
    teller.enqueue(Entity(world), 7.0)
    assert teller.enqueue(Entity(world), 6.0)
    assert not teller.enqueue(Entity(world), 5.0)
    assert len(teller) == 5
    (e, a) = teller.dequeue() or (None, None)
    assert isinstance(e, Entity)
    assert a == 10.0

    world._simulate(tpu=100.0, end_tick=20, realtime=True)
    world._wait()
    world._updateData()
    assert len(plot[0].sources) == 1
    assert plot[0].sources[0] == xydata
    assert xydata.dataset == plot[0]
