# Etlas collector

#### Maintainer: qtomerr@gmail.com

## Terminology
* **Sanjer**: a **Sanjer** is a pre-forked process (or sub-process) that receives serialized runnables and context and executes in the background, reporting back to Redis.
[RQ-dashboard](https://github.com/eoranged/rq-dashboard) can help you manage these remotely.
* Collector: just shorthand for the Etlas collector
* Job ID: a string representing an HMset in Redis, containing all data pertaining to an executed job.

## The basics
The Collector is a job-executor, and the 'how' to the Etlas's 'what'.

It receives a JSON with instructions for executing a task, instantiates a runnable for that task, serializes it and its context and hands it over to a **Sanjer** by means of a Redis proxy.

The **Sanjer** will then execute in the background, updating its Redis key with progress, metadata and status.

In short -
you give a JSON with settings, the Collector will have it done and track progress.

## API
```
GET system/alive
```
```
POST system/alive

Runs basic diagnostics on all connected services (currently only Redis)
```
```
GET platforms/get

Returns a JSON with all available platforms, their required settings, types and default values
```
```
POST execution/run

Requests execution of a task. Returns a Job ID.

Example:
{
    "_id": "devTest",
    "platform_id": "coinis",
    "settings": {
        "start_date": "4 days back",
        "end_date": "yesterday",
        "username": "CoinISUsername",
        "password": "CoinISPassword",
        "storage": {
            "type": "mysql",
            "settings": {
                "hostname": "localhost",
                "db": "selpy_legacy",
                "username": "iamauser",
                "password": "iamapassword",
                "table": "mac_publishers"
            }
        }
    }
}
```
```
GET execution/get?job_id={Job ID}[&full]
Returns all available data on an executed task.

During runtime, platforms may store datasets before and after processing for debugging purposes under the tags 'original' and 'processed'.

This data is removed for performance reasons, unless the 'full' tag is used.
```

## Dev notes
This service aims to be as DRY and flexible as possible.
Just make sure of the following:
* Platforms should be single-class files with type annotations, stored in the 'platforms' directory
* Class parameters are constants. Settings variables are defined in __init__
* All platforms should have a '_run' method as an entry point

The rest should be taken care of automatically.

* Be mindful of adding dependencies, as they may make the entire service heavier.
* Platform encapsulation is critical to the sane function of this system. Don't interconnect stuff.
* In the same spirit, the platform code has been written in a very imperative manner intentionally - it's much easier to debug.
* Encapsulation can also be improved by explicitly serializing the context -
so you could potentially horizontally-scale the **Sanjer**s rather than the entire Collector.
I won't be here to do it, but think about it.