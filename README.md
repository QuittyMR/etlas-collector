# Reflection based scraper

#### Maintainer: [Tomer Raz](qtomerr@gmail.com)

This repository is a remote fork of my HYDI-scaffolder

## Terminology

* **Sanjer**: a **Sanjer** is a pre-forked process (or sub-process) that receives serialized runnables and context and executes in the background, reporting back to Redis.
[RQ-dashboard](https://github.com/eoranged/rq-dashboard) can help you manage these remotely.
* Collector: a complementing service that receives the reflection data from this service and uses it to generate user-serviceable forms
which will provide the necessary data to operate the scrapers.  
* Job ID: a string representing an HMset in Redis, containing all data pertaining to an executed job.

## The basics

This scraper is a job-executor and part of a pair of conjoined services, where this part handles the distributed execution 
and the other handles user-interaction and scheduling.

This service receives a JSON with instructions for executing a task, 
instantiates a runnable for that task, serializes it and its context 
and hands it over to a **Sanjer** by means of a Redis proxy.

The **Sanjer** will then execute in the background, updating its Redis key with progress, metadata and status.

The input JSON's data is stored and delivered by the companion service, 
which generates HTML forms to collect necessary data for execution.
These forms are generated using reflection data provided by this service.

## Why?

This separation allows you to upgrade this service with new code 
without being concerned for availability, persistence or general failure.

Every scraper is completely encapsulated, and is serialized along with its context so 
that it can be executed by any client that registers as a **Sanjer** - so you can collect
a task from anywhere and debug it on your personal computer if need be. 

Any piece of code added to this service is automatically registered, analyzed and is ready
to be instantiated given the correct input from the companion service.

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
    "platform_id": "privatePlatform1",
    "settings": {
        "start_date": "4 days back",
        "end_date": "yesterday",
        "username": "platformUsername",
        "password": "platformPassword",
        "storage": {
            "type": "mysql",
            "settings": {
                "hostname": "localhost",
                "db": "database",
                "username": "iamauser",
                "password": "iamapassword",
                "table": "dbTable"
            }
        }
    }
}
```
```
GET execution/get?job_id={Job ID}[&full]
Returns all available data on an executed task.

During runtime, platforms may store datasets before and after processing for debugging purposes under the tags 'original' and 'processed'.

This data is removed for performance reasons, unless the 'full' flag is used.
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