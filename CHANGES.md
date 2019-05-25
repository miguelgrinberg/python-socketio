# pyton-socketio change log

**Release 4.0.2** - 2019-05-19

- properly handle disconnects from ios client ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c0c1bf8d21e3597389b18938550a0724dd9676b7))
- updated asgi examples to the latest uvicorn ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f86999ff9c3ac5202b017afb9b50036f1f7903a2))
- helper release script ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4632a3522e7e855ca006f797411f02e56291e07d))
- fixed requirements file ([commit](https://github.com/miguelgrinberg/python-socketio/commit/dd3608c79e751940491a2841f8a1b1d63de841dc))
- updated some requirements ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ac7fa5cb5efc750b7d8199fb16557d332f4229d3))

**Release 4.0.1** - 2019-04-26

- remove unused wait and timeout arguments from send method ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fd91e36799b3ba66c0f5ff22504f54b50951833f))
- Add missing import statement for socketio in docs [#289](https://github.com/miguelgrinberg/python-socketio/issues/289) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cacb621ad75b64b7bd740e695446cef5e4f335a2)) (thanks **Syed Faheel Ahmad**!)
- change a typo from `client` to `server` [#280](https://github.com/miguelgrinberg/python-socketio/issues/280) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/55e3a6cb02471adff9fa6cd45774003f778b6db4)) (thanks **Almog Cohen**!)
- add link to stack overflow for questions ([commit](https://github.com/miguelgrinberg/python-socketio/commit/65c4675bab7f40a2c446428f1f7ba4faa85c659a))
- Merge branch 'Keylekan-master' ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3af9a003aa63259bfe4dd7ae25b1bcefc627507a))
- Add namespaces parameter to the self.connect call in the reconnection process ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c4e4b0b226390a48e4ff9e73a60ff85f68cb9c4c)) (thanks **quentin**!)

**Release 4.0.0** - 2019-03-09

- change async_handlers default to true, and add call() method ([commit](https://github.com/miguelgrinberg/python-socketio/commit/88dcf7d414baec32d6f9f5571d1c03cb09e75c65))
- Add ConnectionRefusedError and handling for it ([commit](https://github.com/miguelgrinberg/python-socketio/commit/38edd2c93950d85d97258c104af24792b01dc1e3)) (thanks **Andrey Rusanov**!)
- fix python 2 unit test ([commit](https://github.com/miguelgrinberg/python-socketio/commit/9ddc860391ba1b0ea8a43d16d2865e1422346eda))
- client disconnect does not take namespace as argument [#259](https://github.com/miguelgrinberg/python-socketio/issues/259) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c35451421d2754c09c101c56590152d13cc8b0ea))
- Avoid double calls to client disconnect handlers [#261](https://github.com/miguelgrinberg/python-socketio/issues/261) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f752312884332e86946df0c4c60ee52dd0590164))
- readme fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/1fb1f6d6e5a25159e9c1f35b005098e05a4a18e4))
- Update sanic version in requirements.txt [#255](https://github.com/miguelgrinberg/python-socketio/issues/255) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6e4079ac64c1c69843fd5b2a9c735bb46671b5bf)) (thanks **maxDzh**!)
- simplify client dependencies ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d28eff7013c084c4f3c491a146bbec35acb18560))

**Release 3.1.2** - 2019-01-30

- Type in documentation [#241](https://github.com/miguelgrinberg/python-socketio/issues/241) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3c08dda918dd1985c2f10174e7b54f031908099b)) (thanks **Emeka Icha**!)
- fix typo with quotes in doc [#238](https://github.com/miguelgrinberg/python-socketio/issues/238) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a5a67120fec2211002915e8bbcff1c034a5eb93f)) (thanks **Julien Deniau**!)

**Release 3.1.1** - 2019-01-09

- do not use six in setup.py ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b4512b13176b6c04e29803759fff346ca78eb76f))

**Release 3.1.0** - 2019-01-03

- unit test reorganization ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b0a8b1f31bce4305c00ab0937ddfec1120a2d49d))
- user sessions ([commit](https://github.com/miguelgrinberg/python-socketio/commit/9f2186725adba33b634f7287e3518086e2bbc3ea))

**Release 3.0.1** - 2019-01-01

- correct handling of disconnects [#227](https://github.com/miguelgrinberg/python-socketio/issues/227) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/45d880cf905f05e1c9966fbe46ed53236bda2851))

**Release 3.0.0** - 2018-12-22

- SocketIO client
- reorganization of examples, plus some new ones for the client ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4822d8125df11bbf2ef3061c0622164f37a261c9))
- minor example code fix ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fc5fbcf005f750a67d6aeb7bbd190125ea7970fd))
- resolve wrong variable and css element [#177](https://github.com/miguelgrinberg/python-socketio/issues/177) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/251b5be9dfc5d88a3bbf146ff52197863d5ce109)) (thanks **iepngs**!)

**Release 2.1.2** - 2018-12-10

- update dependencies ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f642a7f2078fc639ed1302b5b3f7133f19c629c6))

**Release 2.1.1** - 2018-12-05

- fix backwards compatible problems with python-engineio 3.0 ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fce2006eeef2528e9b59ce9097ff215e6117d787))

**Release 2.1.0** - 2018-11-26

- ASGI support ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b214380d056dbbfb08273ac482633254176cb847))
- Fix synchronization issue in SocketIO [#213](https://github.com/miguelgrinberg/python-socketio/issues/213) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4a030d2f9c812b2dd0237883b072189feccac9b7)) (thanks **Anthony Zhang**!)
- Logging improvements for write-only connections [#197](https://github.com/miguelgrinberg/python-socketio/issues/197) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/da7cb863301524aead8c4c422491e84c5a1c10bc)) (thanks **Kelly Truesdale**!)
- improved documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/87fb830bd803809a6577332a838285b4bc22dce5))
- updated dependencies and fixed linter error ([commit](https://github.com/miguelgrinberg/python-socketio/commit/015ea2037f8fb75c35f8478d14628bf91c54e603))
- better handling of packets with no data ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f2d28ad62caa4ea6374bf9330b4ad7c79eaf2e05))
- add python 3.7 to tox ([commit](https://github.com/miguelgrinberg/python-socketio/commit/1777c527781f788571e4f8a1f8e1f0d813ea9b8b))
- Tornado examples readme ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2a8befdbc9e4fa47a355bf2919319df47b30c973))
- Tornado docs ([commit](https://github.com/miguelgrinberg/python-socketio/commit/415af129b756d5e955180af314589bdc0c5930ff))

**Release 2.0.0** - 2018-06-28

- Tornado 5 support ([commit](https://github.com/miguelgrinberg/python-socketio/commit/555b69e80754ceb90d7c7aab1825cc37724b2e90))
- Fix typo in docs [#187](https://github.com/miguelgrinberg/python-socketio/issues/187) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/58c8a6f4301758ff27fb95d28b939bf953a67119)) (thanks **Grey Li**!)
- Update documentation link [#185](https://github.com/miguelgrinberg/python-socketio/issues/185) Pythonhosted.org was deprecated. ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4131e539f8b480ecd11f0c03239a5359a3012e34)) (thanks **Grey Li**!)
- typo fix [#180](https://github.com/miguelgrinberg/python-socketio/issues/180) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c24c91a72521eeb19eb5ee60e06006da5e8c7578)) (thanks **Toon Knapen**!)
- add pypy3 target to travis builds ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ad37d0db930edf773221cfad40582618c821cb48))

**Release 1.9.0** - 2018-03-07

- assigning local ret variable to none if the asyncio task is canceled [#164](https://github.com/miguelgrinberg/python-socketio/issues/164) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/598568c7152dc970dc740de040697e97cf374ec1)) (thanks **rettier**!)
- Recoonect to redis when connection is lost [#143](https://github.com/miguelgrinberg/python-socketio/issues/143) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/af13ef067c0f5b357e80d0e7f718bb725ed55fd6))

**Release 1.8.4** - 2017-12-11

- properly handle callbacks in multi-host configurations for asyncio ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b3fc842c76d53c2632192c5fda3db42a0bb764cd))
- Properly handle callbacks in multi-host configurations [#150](https://github.com/miguelgrinberg/python-socketio/issues/150) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8d7059a1a22e2d5e3092623251ab357046595a33))
- aiohttp instead of flask in example HTML [#91](https://github.com/miguelgrinberg/python-socketio/issues/91) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/06e7cece74b01707247d28537537eafd73d96f02)) (thanks **Jacopo Farina**!)
- Fix backquotes usage in docs. [#146](https://github.com/miguelgrinberg/python-socketio/issues/146) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ef7088d67a5b26fa57f921797057622f6525f768)) (thanks **Kane Blueriver**!)
- updated socketio js client to v2.0.4 in all examples ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8415a7a33c324ee70002bf8893bb388768fd5cb1))

**Release 1.8.3** - 2017-11-13

- fixed memory leak on rejected connections for asyncio ([commit](https://github.com/miguelgrinberg/python-socketio/commit/935077563490f890f1b1d596be9fc38c8d65588b))

**Release 1.8.2** - 2017-11-13

- fixed memory leak on rejected connections [#574](https://github.com/miguelgrinberg/Flask-SocketIO/issues/574) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/66e17fb387510522bc9a1718ae9da8b0f6ace005))

**Release 1.8.1** - 2017-10-02

- JavaScript client sends query string attached to namespace [#124](https://github.com/miguelgrinberg/python-socketio/issues/124) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7f02f7aaa92c18c043466cb4721356221361f481))
- Update README.rst ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8bba811408b2e3a570701b34113a53662915f97c))
- Documented protocol defaults ([commit](https://github.com/miguelgrinberg/python-socketio/commit/187c52582ba4a3c08a368e6b5f4033a417a432f1))

**Release 1.8.0** - 2017-07-26

- Made queues non-durable. Always retry after disconnect. [#120](https://github.com/miguelgrinberg/python-socketio/issues/120) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/358a8e118fe73920fb7e0b72811f14c0daedeea2)) (thanks **Alex Plugaru**!)

**Release 1.7.7** - 2017-07-20

- pass redis password in the URL ([commit](https://github.com/miguelgrinberg/python-socketio/commit/af811326103abf90338987a326190df210c421af))
- redis pub/sub support set password [#116](https://github.com/miguelgrinberg/python-socketio/issues/116) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8cf035fb3a13651060f7241c3460e3339891e1e5)) (thanks **larry.liu**!)

**Release 1.7.6** - 2017-07-02

- async_handlers option for asyncio servers ([commit](https://github.com/miguelgrinberg/python-socketio/commit/93f70dc9e1e9bc4cb13f631edc4c12cf110356b7))
- fixed requirements file for python 2 ([commit](https://github.com/miguelgrinberg/python-socketio/commit/690be4fd194747593ab44acd0a1ea4de5dbcbfa4))
- minor improvements to django example ([commit](https://github.com/miguelgrinberg/python-socketio/commit/1ecbf5bef0c16d5665f72fad205af3ad45679ae4))
- Django example ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3531b513a845a5bcac1b7ae511aeb71e19de7256))

**Release 1.7.5** - 2017-05-30

- validate namespace in disconnect call [#427](https://github.com/miguelgrinberg/Flask-SocketIO/issues/427) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3ae013b90e1915a99abe8ca0b7ed8611cc4203d2))
- The usage of class-based namespace There should be an additional `self` argument passed to each member function of custom Namespaces. ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8e734573a9f792d8dbfb143cba1f10056930f0e9)) (thanks **Kaiyu Shi**!)
- fix misleading error message ([commit](https://github.com/miguelgrinberg/python-socketio/commit/36f8d35d08a29298b8e4acefb7bb7ba67bddf54c))

**Release 1.7.4** - 2017-03-28

- Handle broadcasts to zero clients [#88](https://github.com/miguelgrinberg/python-socketio/issues/88) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/af0004d78edda2da1d9bbcab9742ca75976d4373))

**Release 2.7.3** - 2017-03-22

- Fix variable referenced before assignment [#85](https://github.com/miguelgrinberg/python-socketio/issues/85) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5b9b17c4a0654811aeda4184d159dafb5e0e4041))
- use Python 3.6 for docs build ([commit](https://github.com/miguelgrinberg/python-socketio/commit/142e4787375782c74d6d0b992115269dc290069b))

**Release 1.7.2** - 2017-03-08

- websocket support for sanic ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2582f286f592c881fefeed0b639edecd41d81e4c))

**Release 1.7.1** - 2017-02-15

- Fixed initialize() method in PubSubManager subclasses [#406](https://github.com/miguelgrinberg/python-socketio/issues/406) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5e1391d80ee2e6b215819ea00df4d166f0ae3f0b))
- Update README.rst Spelling correction ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d6839e9ae833bbb5aa8bbaff1e907c1869fdfc59)) (thanks **Ken W. Alger**!)
- sanic examples (long-polling only) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/38af61ee1f3fa2b76c87e12e83077a9b20156db9))
- fixed link in readme file ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ea94110559c3ada0b1a78e57f72fd3e6a8f0c34e))

**Release 1.7.0** - 2017-02-12

- redis message queue for asyncio ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ce44133acd66d53d607937d04261668fbc2aa328))
- updated documentation logo ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2e55d7f0208fe0679fd87081c9598640a14c2fdb))
- asyncio documentation and various fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/43788db7a77421ec9f84f1eb02b60f9bc09d29d3))
- readme file updates ([commit](https://github.com/miguelgrinberg/python-socketio/commit/83379732f9a597d248c9f191304fcfbf1622b7b6))
- updated public symbols ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3556c3e7ce547e0d49255e883db3128fdf9974b6))
- updated package requirements ([commit](https://github.com/miguelgrinberg/python-socketio/commit/561065141a8121f544a718530ed87bced46ed529))
- readme files and requirements for all examples ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5c882acd884271a9fa05ab3397e872ddaa1235a5))
- async namespaces, and more unit tests ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6f41206f7dfda01a8ad3d75110eb1022b6b768f3))
- a few asyncio related fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/763583226a91505051889ac3b23bf1183aa6c421))
- asyncio support ([commit](https://github.com/miguelgrinberg/python-socketio/commit/53d10d9f3204a86b8c48ffca347857044215d009))
- fixed documentation typo [#19](https://github.com/miguelgrinberg/python-socketio/issues/19) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6c93f7fb15e5848de48daefe5998139734333dd9))
- minor fixes to zeromq support ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f0f6b18f42c7b9a2d4f9806b854849ae2202d547))
- use non-blocking eventlet zmq wrapper in listen method ([commit](https://github.com/miguelgrinberg/python-socketio/commit/10d273b3feee216ea711689004454e87c3b237bc)) (thanks **Eric Seidler**!)

**Release 1.6.3** - 2017-01-23

- allow event names with hyphens [#51](https://github.com/miguelgrinberg/python-socketio/issues/51) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/940d262a1ed9b45969895b93b7184f93bdab71b9))
- Merge branch 'Kurlov-fix-namespace-hyphens' ([commit](https://github.com/miguelgrinberg/python-socketio/commit/923ded03b2fba18ee84491d11b5059eefa81cc99))
- Fixed hyphens namcespace bug ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4f35e67e42fad8b75d9f755a00141d5ef86eb76d)) (thanks **Aleksandr Kurlov**!)
- removed py33 from tests, added py36 ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3c868255a481ef17deb53f022e668a60957a2f17))
- handle failed pickled.loads ([commit](https://github.com/miguelgrinberg/python-socketio/commit/42ad98e750afd91847f65a7221de665da6585495)) (thanks **Eric Seidler**!)
- check message type before yielding message data ([commit](https://github.com/miguelgrinberg/python-socketio/commit/09d8d5d0d40d71e246d5c1a1ba8d2375b591f833)) (thanks **Eric Seidler**!)
- add zmq prefix to default value for url ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fab0683bebbc550d9e9fef418baa07fc510f71d0)) (thanks **Eric Seidler**!)
- add zmq manager ([commit](https://github.com/miguelgrinberg/python-socketio/commit/88f3b87efa9f91d1e6eb23a110962d8d664ff1c3)) (thanks **Eric Seidler**!)
- add ZmqManager to dunder init ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d6f703f1bd36b1a68e0e555212ef128fef3aacad)) (thanks **Eric Seidler**!)

**Release 1.6.2** - 2017-01-03

- prevent binary attachments from getting mixed up Flask-SocketIO issue [#385](https://github.com/miguelgrinberg/python-socketio/issues/385) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2c98906aafc53ae84e6fe7492ca6f1f48115ce58))
- Merge branch 'AndrewPashkin-clarify-level-of-separation-of-namespaces' ([commit](https://github.com/miguelgrinberg/python-socketio/commit/652ced75c010877e5b2566f61e9ce2098869dc0d))
- Add mentioning of SIDs to the list of what each namespace has separate from other namespaces. ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8a7ea67f99f23d5b83274bda62d6345108d022be)) (thanks **Andrew Pashkin**!)

**Release 1.6.1** - 2016-11-26

- Added "ignore_queue" option to bypass message queue in emits ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3eac53261b9d602da8d27c1f9b31f92f86a3b395))
- Use a statically allocated logger by default ([commit](https://github.com/miguelgrinberg/python-socketio/commit/749f8663c48cf100440ba51724542577e46c1b58))
- Warn when message queues are used without monkey patching ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6ba131af5cf6238fe4a4a702b38dfec2bb1292f9))
- Added clarification regarding class based namespace being singletons [#59](https://github.com/miguelgrinberg/python-socketio/issues/59) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d09627faff80e78b92a27ec8f8c46a846002e873))
- Fix typo Sokcet -> Socket [#56](https://github.com/miguelgrinberg/python-socketio/issues/56) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/415a0eb9c7d4105d75f569e455b8f293dc6540c4)) (thanks **Lenno Nagel**!)

**Release 1.6.0** - 2016-09-25

- some improvements and optimizations to KombuManager class ([commit](https://github.com/miguelgrinberg/python-socketio/commit/052fd937453dc098761dba10c7240c39bdb5d750))
- add a TTL option to Kombu queues when RabbitMQ is used ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cc9027586f045b6aa96e832bb287971762fb339d))
- put clients in a pre-disconnect state while their disconnect handler runs This avoids potential endless recursion. [#312](https://github.com/miguelgrinberg/Flask-SocketIO/issues/312) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/da2d141e8d68fd698ddb2dd5d54c4b1a7622d4df))
- do not disconnect an already disconnected client [#312](https://github.com/miguelgrinberg/Flask-SocketIO/issues/312) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a58c184b0ffe76d8b00912b0084b12c26bd85631))

**Release 1.5.1** - 2016-09-04

- add __version__ to package ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b436d60a9ffe787a25e284046d32f5d9f8c18f58))
- document the use of the new gevent_uwsgi async mode ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5529fbb2bd13654ed34094629bf77250ccf60167))

**Release 1.5.0** - 2016-08-26

- add async_handlers option to server ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2d39058b7c693bf74c8e3169d72c21a5597d73d8))
- minor class-based namespace fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/214abc8d31927673d9b853cf6a901cec1f3988ea))
- minor documentation fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5cc91993369c33ea090782dba1256cce90140295))
- class-based namespaces ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7bc329a12d9f9b4ad4953dc74505167ee4dd5f57))
- minor correction in the readme file example ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6abd86fd868ae4bd5e23b02401f638ec1d0bad2c))
- Update README.rst Add the code highlight to python ([commit](https://github.com/miguelgrinberg/python-socketio/commit/44b1acb6973882be9c89e48e6f187de7aecef8e9)) (thanks **Rodolfo Silva**!)
- add explicit eventlet.wsgi import ([commit](https://github.com/miguelgrinberg/python-socketio/commit/33bd933d8b6c5926c751d6a83f38a2ab7e524b36))
- Handle empty argument list for callbacks [#26](https://github.com/miguelgrinberg/python-socketio/issues/26) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/544b01ad3df74cd92199c251292d6a8fdb09f47b))

**Release 1.4.4** - 2016-08-05

- minor documentation improvement ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c52f4f6a594f91fc69473d492c0e3117b32de21e))
- Fix race condition in handling of binary attachments [#37](https://github.com/miguelgrinberg/python-socketio/issues/37) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/024609e10e570ccd2e932a0584c5a1784c4bbf75))
- release 1.4.3 ([commit](https://github.com/miguelgrinberg/python-socketio/commit/047712da097b44812d09a88537c6877757b25eba))
- Do not allow event names with hyphens in them [#36](https://github.com/miguelgrinberg/python-socketio/issues/36) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a6838a233d051b406baeb9a4c09e50f62bc9f14a))
- add unit test for sleep function ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a3ae2a938472f103d543ad46ff6d923c0f2415ee))

**Release 1.4.2** - 2016-07-12

- fix the order of triggered disconnect event [#33](https://github.com/miguelgrinberg/python-socketio/issues/33) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ea1a52ac84cf2cd3d5cb6d1c0f6a64932159d835)) (thanks **Hanzawa Ye**!)
- Correct sio.emit() call in readme [#32](https://github.com/miguelgrinberg/python-socketio/issues/32) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a1ca2c421c4f2f05e83372e4dac0b3826be66d16)) (thanks **winek**!)

**Release 1.4.1** - 2016-06-28

- pass return value of start_background_task to the caller ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cd9e1a7c6427eb6e13abea15d84dfc692f843df2))
- a few improvements to examples ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0810f0b039753d9c98f83eebf5a1b183aabd6d49))

**Release 1.4** - 2016-06-28

- a few improvements to examples ([commit](https://github.com/miguelgrinberg/python-socketio/commit/20185c9a95bcd1ab4d4457b483cf6172eaf020c2))
- expose async_mode and sleep from engineio ([commit](https://github.com/miguelgrinberg/python-socketio/commit/065cc4b2219d22f7b470600073f21c47c09d5578))

**Release 1.3** - 2016-05-15

- delay start of message queue listener thread until first request comes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b6df63d8492c9a18e7d4a7ea5e8378e076b7a723))
- Avoid KeyError when no room exists [#27](https://github.com/miguelgrinberg/python-socketio/issues/27) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/626499cd4596c13a41a5ecbe3e350b243c5fe6be)) (thanks **Patrick Decat**!)

**Release 1.2** - 2016-03-21

- Avoid KeyError in is_connected. [#22](https://github.com/miguelgrinberg/python-socketio/issues/22) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cba6c3ed8b8b2c777538a5a35e73f98f4ec9d4bb)) (thanks **Chris Doehring**!)

**Release v1.1** - 2016-03-06

- remove disconnected client before invoking disconnect handler ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d34f49b3b19c39f0beaed9d0e762f070b71f7104))
- Eliminate problematic _clean_rooms method ([commit](https://github.com/miguelgrinberg/python-socketio/commit/370db6488bfee5db9d90d675fd0ed8fae9baab0d))
- handle leaving a room and entering again right after [#17](https://github.com/miguelgrinberg/python-socketio/issues/17) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/74e9ab11dcaef919cba198aef6b8124dcfc3007c))
- document the need to monkey patch with eventlet and gevent ([commit](https://github.com/miguelgrinberg/python-socketio/commit/dabe33f1a1d332649f42c9adfd9e5ec15501e64c))

**Release 1.0** - 2016-01-17

- Expand tuples to multiple arguments, but not lists ([commit](https://github.com/miguelgrinberg/python-socketio/commit/259f98d3cdc7274007c7ad4781979cc108b667f2))

**Release 0.9.2** - 2016-01-16

- silence a flak8 error on imports not at top ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ba31975d65108c106d9193277441e8acad18baf9))
- Use separate read and write Kombu connections Eventlet does not like file handles to be shared among greenlets. Using an independent connection in the listening thread addresses this problem. [#13](https://github.com/miguelgrinberg/python-socketio/issues/13) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0c357573599e687137ba2e8648b2cac49c8b7bbb))

**Release 0.9.1** - 2016-01-10

- Pass result of connect handler up to engineio ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d8982dba81fe56a16e10f80b01e5f262e4b3b0ae))

**Release 0.9.0** - 2016-01-10

- Add write_only argument to Kombu and Redis manager classes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/57756e3bdcc025e1bc31f67f8a44c0b38fc3747c))
- minor message queue documentation improvements ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0e47a75a3a937beed271a797cc8dbda1eb6c9de1))

**Release 0.8.2** - 2015-12-30

- correct kombu implementation of a fanout queue ([commit](https://github.com/miguelgrinberg/python-socketio/commit/73fd49903387725b47498625005a6a1b13ff6948))

**Release 0.8.1** - 2015-12-14


**Release 0.8.0** - 2015-12-14

- documentation updates ([commit](https://github.com/miguelgrinberg/python-socketio/commit/e56ff807f4faabb4e7ef339fda79de5b8a201b26))
- do not allow callbacks outside of a server context ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6ae89688d72ec7f570a0b04a1bbf0483865bb5b5))
- message queue documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8ee4cf7e7557aeb02079c8402029eec5b68c79b6))
- pubsub unit tests ([commit](https://github.com/miguelgrinberg/python-socketio/commit/71142aa2db1434ab799edebeaa97020c6ec21089))
- README typo fix Important typo fix in README example code. ([commit](https://github.com/miguelgrinberg/python-socketio/commit/71e99d9a6b0804942bb9e507b3ce984143bee3ba)) (thanks **Davis Miculis**!)
- Support for callbacks across servers ([commit](https://github.com/miguelgrinberg/python-socketio/commit/63f5ed3429f96afd8f3a7cd82f281c2e5db93de1))
- initial implementation of inter-process communication ([commit](https://github.com/miguelgrinberg/python-socketio/commit/47620bbebd92a1b388df72a88c0ca35cdb530073))

**Release 0.7.0** - 2015-11-22

- Correctly handle payloads that are empty lists or dictionaries [#5](https://github.com/miguelgrinberg/python-socketio/issues/5) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a72f2dfb052d1f60a81edf1bb783c7aa4562f124))
- Added python 3.5 to the tox build ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3cb904cfd83f7407b2e6317b349bea925c7333a4))

**Release 0.6.1** - 2015-10-31

- support packets with empty payload given as an integer ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d31d167c78203732c74a97f5a98788462231e01f))

**Release 0.6.0** - 2015-10-17


**Release 0.5.2** - 2015-09-22

- fixed regression introduced in latest release with ack ids ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4a4ba41d0c7c6c5547fc73065ab2279ca7fce76b))

**Release 0.5.1** - 2015-09-16

- Cleaned up the interface to provide a custom client manager ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5bb6c9da7df017318975d35e1221056ea5670d2d))
- Move ack functionality into BaseManager class ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ad12b837be360d4d9dbe1a1e5e1afdb573ab335d))

**Release 0.5.0** - 2015-09-02

- Added a latency check example ([commit](https://github.com/miguelgrinberg/python-socketio/commit/798c126d76247d9b41d07bf30aaa41d5daea63bb))
- Fix executable bits in several files ([commit](https://github.com/miguelgrinberg/python-socketio/commit/171008023e3662ba5375c3c76cc7629a4620eaa1))
- Added transport method to server class ([commit](https://github.com/miguelgrinberg/python-socketio/commit/37cd746a8eac8a23c6b3e396a2ae48510fcdb974))
- Updated example requirements ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a1e232f8c77f0599fd53dc2b683b133436dda5a9))
- Allow application to provide a custom JSON encoder/decoder. ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f3967320883f8e5d41df0cc69475fa89eb6357aa))

**Release 0.4.2** - 2015-08-23

- Improved handling of logging ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4cb515136336864de0012595963341f81f262dc7))
- Updated example app to use gevent websocket if available ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7b2e4ab88789a52f1e91be538a1b5da6fb8dff02))

**Release 0.4.1** - 2015-08-20

- Added docs on websocket support with gevent ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b59cefcfdb42e13646b4f1bee50e483935b8e57c))
- Fixed executable bit on several files ([commit](https://github.com/miguelgrinberg/python-socketio/commit/9cee03859c69cfb5aac37dac4163e852bec7e8e0))

**Release 0.4.0** - 2015-08-08

- Added support for gevent and standard threads besides eventlet ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8e570789aabb90fd494d6468a5512d631e56d60f))
- added server disconnect support ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5633917201825366771011e10d7a3df3d2dc8a75))

**Release 0.3.0** - 2015-07-27

- allow events to be sent from the connect handler ([commit](https://github.com/miguelgrinberg/python-socketio/commit/19042e157061345938450bcd9d098ffbef2acecd))

**Release 0.2.0** - 2015-07-20

- Return the rooms a client is in ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d4cd9de799726a8ed6f0d30e15c9bf80047d7de6))
- Added build files ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7195217b3bb087530dc1cd080b69e4cc7f5c6914))
- Initial commit ([commit](https://github.com/miguelgrinberg/python-socketio/commit/aa2e146a60aa9b2257ce748690104c796a09b551))
