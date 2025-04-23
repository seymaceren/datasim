from datasim import Dashboard, World, simulation


def test_world_headless():
    World.reset()
    world = World(headless=True)
    assert world.title == "Unnamed Simulation"
    assert simulation.tps == 10.0
    assert world.headless
    world.simulate(end_tick=100)
    world.wait()
    world = World()
    assert simulation.ticks == 100
    assert simulation.time == 10.0


def test_world_dashboard():
    World.reset()
    dashboard = Dashboard()
    dashboard._draw()
    assert not hasattr(dashboard, "plots")
    world = World("TEST TITLE", 0.5)
    assert world.title == "TEST TITLE"
    assert simulation.tps == 0.5
    assert not world.headless
    assert world.simulate(tps=1.0, end_tick=20)
    world.wait()
    assert not world.simulate(tps=1.0, end_tick=20)
    world.stop()
    assert world.stopped
    world2 = World("NEW WORLD")
    assert not hasattr(world2, "title")
    assert simulation.world() == world
    assert simulation.ticks == 20
    assert simulation.time == 20.0
