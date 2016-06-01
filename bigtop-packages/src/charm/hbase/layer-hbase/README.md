# HBase Overview

HBase is the Hadoop database. Think of it as a distributed scalable Big Data
store.

Use HBase when you need random, realtime read/write access to your Big Data.
This project's goal is the hosting of very large tables -- billions of rows X
millions of columns -- atop clusters of commodity hardware.

HBase is an open-source, distributed, versioned, column-oriented store modelled
after Google's Bigtable: A Distributed Storage System for Structured Data by
Chang et al. Just as Bigtable leverages the distributed data storage provided
by the Google File System, HBase provides Bigtable-like capabilities on top of
Hadoop and HDFS.

HBase provides:

- Linear and modular scalability.
- Strictly consistent reads and writes.
- Automatic and configurable sharding of tables
- Automatic failover support between RegionServers.
- Convenient base classes for backing Hadoop MapReduce jobs with HBase tables.
- Easy to use Java API for client access.
- Block cache and Bloom Filters for real-time queries.
- Query predicate push down via server side Filters
- Thrift gateway and a REST-ful Web service that supports XML, Protobuf,
  and binary data encoding options
- Extensible jruby-based (JIRB) shell
- Support for exporting metrics via the Hadoop metrics subsystem to files
  or Ganglia; or via JMX.

See [the homepage](http://hbase.apache.org) for more information.

This charm provides the hbase master and regionserver roles as delivered by the
Apache Bigtop project.


## Usage

A HBase deployment consists of HBase masters and HBase RegionServers.
In the distributed HBase deployment this charm provides each unit deploys
one master and one regionserver on each unit. HBase makes sure that
only one master is active and the rest are in standby mode in case
the active one fails. 

To HBase operates over HDFS so we first need to deploy::

    juju deploy hadoop-namenode namenode
    juju deploy hadoop-slave slave
    juju deploy hadoop-plugin plugin
    juju deploy openjdk

    juju add-relation namenode slave
    juju add-relation plugin namenode
    juju add-relation namenode openjdk

In order to function correctly the hbase master and regionserver services
have a mandatory relationship with zookeeper - please use the zookeeper charm
to create a functional zookeeper quorum and then relate it to this charm::
Remember that quorums come in odd numbers start from 3 (but it will work
with one BUT with no resilience).

    juju deploy hadoop-zookeeper zookeeper
    juju add-units -n 2 zookeeper

Now we are ready to deploy HBase scale it and add the required relations.

    juju deploy hbase
    juju add-units -n 2 hbase

    juju add-relation zookeeper hbase
    juju add-relation openjdk hbase
    juju add-relation plugin hbase

The charm also supports use of the thrift gateway.

## Service Restarts

Restarting a HBase deployment is potentially disruptive so you should be aware
what events cause restarts::

- Zookeeper service units joining or departing relations.
- Upgrading the charm or changing the configuration.


## Smoke Test

You can smoke test your deployment using the smoke test action:

    juju action do hbase/0 smoke-test

After a few minutes, you can check the outcome of the test:

    juju action status

The execution log of the performance test triggered by smoke test
is kept under /opt in the unit where the action was submitted to.


## Contact Information
- <bigdata@lists.ubuntu.com>

## Help
- [Apache HBase home page](https://hbase.apache.org/)
- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
