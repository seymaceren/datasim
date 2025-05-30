from datasim import Dashboard, logging, LogLevel, Runner, World


def test_world_headless():
    logging.level = LogLevel.debug
    runner = Runner(World, True)
    world = runner.worlds[0]
    assert world.title == "Unnamed Simulation"
    assert world.tpu == 10.0
    assert world.headless
    world._simulate(end_tick=100)
    world._wait()
    _ = World(runner)
    assert world.ticks == 100
    assert world.time == 10.0


def test_world_dashboard():
    logging.level = LogLevel.debug
    dashboard = Dashboard()
    dashboard._draw()
    assert hasattr(dashboard, "plots")
    runner = Runner(World)
    world = runner.worlds[0]
    world.tpu = 0.5
    assert world.tpu == 0.5
    assert not world.headless
    assert world._simulate(tpu=1.0, end_tick=20)
    world._wait()
    assert not world._simulate(tpu=1.0, end_tick=20)
    world._stop()
    assert world.stopped
    world2 = World(runner, "NEW WORLD")
    assert hasattr(world2, "title")
    assert runner.worlds[0] == world
    assert world.ticks == 20
    assert world.time == 20.0
