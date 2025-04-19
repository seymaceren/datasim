from datasim import (
    Entity,
    Plot,
    Queue,
    QueuePlotData,
    Resource,
    ResourcePlotData,
    World,
    XYPlotData,
)


def test_plot():
    World.reset()
    world = World("Plot test", 0.5)

    xydata = XYPlotData()
    plot = Plot("plot1", xydata)
    xydata.append(10, 20)
    xydata.append(20, 50)
    xydata.append(30, 30)
    assert xydata._buffer_index == 3
    world.add_plot(plot)

    water = Resource(world, "water", "water", 0, 0.0, 0, 1000.0, 100.0)
    assert water.amount == 100.0
    world.add(water)
    world.add_plot(Plot("plot2", ResourcePlotData("water")))

    teller = Queue("teller", 5)
    assert teller.capacity == 5
    assert len(teller) == 0
    world.add(teller)
    teller.enqueue(Entity(), 10.0)
    teller.enqueue(Entity(), 9.0)
    teller.enqueue(Entity(), 8.0)
    teller.enqueue(Entity(), 7.0)
    assert teller.enqueue(Entity(), 6.0)
    assert not teller.enqueue(Entity(), 5.0)
    assert len(teller) == 5
    (e, a) = teller.dequeue()
    assert isinstance(e, Entity)
    assert a == 10.0
    world.add_plot(Plot("plot2", QueuePlotData("teller")))

    world.simulate(tps=100.0, end_tick=20, realtime=True)
    world.wait()
    world._draw()
    assert len(plot.data) == 1
    assert plot.data[0] == xydata
    assert xydata.plot == plot
