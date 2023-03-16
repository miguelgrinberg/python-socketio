# python-socketio change log

**Release 5.8.0** - 2023-03-16

- Made kombu client manager more robust and efficient ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8293dc3f8fa90f3d92192a702b28c23d8c516110))
- Made aio_pika client manager more robust and efficient [#1142](https://github.com/miguelgrinberg/python-socketio/issues/1142) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cd7f781c022dd1d1ec3c6695a0fd6ab3ce864fd5))
- Correctly handle emits to multiple rooms in the async server [#1081](https://github.com/miguelgrinberg/python-socketio/issues/1081) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/232cef1f86ff19878190c44caf991e017c8480a4))
- Expose the `ignore_queue` option in namespaces [#1103](https://github.com/miguelgrinberg/python-socketio/issues/1103) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/1cadada02dd7dc1eb96f45e88cbec67e1a393db3))
- Do not automatically import zmq ([commit](https://github.com/miguelgrinberg/python-socketio/commit/de4d5b51e5fc8ba0d0f904851f23f8cced16d7f6))
- TLS/SSL client documentation [#1040](https://github.com/miguelgrinberg/python-socketio/issues/1040) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/54aecfda917ec100e0b5e2c0e955ef719e0eb645))
- Removed incorrect reference to multiple callback invocations in documentation [#1152](https://github.com/miguelgrinberg/python-socketio/issues/1152) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c4117fd6514374042127ab05f1f2d8d221fcf60d))
- Fix documentation typo [#1155](https://github.com/miguelgrinberg/python-socketio/issues/1155) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/270eb372cc83778a897d32e95453eb385328d9de)) (thanks **Onwuka Gideon**!)
- Fix documentation typos ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8c747ab67b3e5c9f31db540a13c3da1b7784617c))
- Fix documentation typo in asyncio_server.py [#1150](https://github.com/miguelgrinberg/python-socketio/issues/1150) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b2cc86cfb2502691d70447b0002179602a798e77)) (thanks **riz-j**!)
- Fix documentationi type [#1091](https://github.com/miguelgrinberg/python-socketio/issues/1091) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/55db7458900a179a9363294cc4fc91eb9c775f54)) (thanks **mostlycryptic**!)
- Add Python 3.11 to builds ([commit](https://github.com/miguelgrinberg/python-socketio/commit/60fe63b098af8c035891ae62a4336538ea419184))

**Release 5.7.2** - 2022-10-17

- Fixed disconnect implementation when using a message queue [#1002](https://github.com/miguelgrinberg/python-socketio/issues/1002) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f56ef6f0401b273107fc483c4ae1b5512209ac48))
- Fixed remote async disconnects via message queue [#1003](https://github.com/miguelgrinberg/python-socketio/issues/1003) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/104d6569a0480ed0adb04e7d41f156762f9ebe9b))
- Support optional payloads in msgpack implementation [#981](https://github.com/miguelgrinberg/python-socketio/issues/981) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ce1afd79e69e35b81a6f0d02fbd7ae04af59f9d6)) (thanks **Cromfel**!)
- Recommend ASGI integration for Sanic in Documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2c3e360ae8b151bc0bfedbde50248cd0dc8d1ff9))

**Release 5.7.1** - 2022-07-15

- Add `namespaces` argument to `Server` and `AsyncServer` [#822](https://github.com/miguelgrinberg/python-socketio/issues/822) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/efe87d867a205493654107d381bdb8b619b8ab2d))
- Add missing `await` in asyncio server [#952](https://github.com/miguelgrinberg/python-socketio/issues/952) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d4e69fb7ceecdb98584f36e085a186eb4da23b07)) (thanks **sjrodahl**!)

**Release 5.7.0** - 2022-07-04

- Server refuses connections on unknown namespaces [#822](https://github.com/miguelgrinberg/python-socketio/issues/822) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/44715012dc0d578b067a9a389c8aef2ce39f65c1))
- Do not send ACK packet for unknown events [#824](https://github.com/miguelgrinberg/python-socketio/issues/824) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/268fe12ffa68f7af8881c75695c287c09490cef9))
- Fix Python 3.11 deprecation warning [#941](https://github.com/miguelgrinberg/python-socketio/issues/941) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4b697815c3da4574fca8b759d21a4e0800dafc50)) (thanks **Jérôme Boulmier**!)
- Correct handling of RedisError exception [#919](https://github.com/miguelgrinberg/python-socketio/issues/919) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/98318fbdde2c4dcfba15d1b0aaf266b599e81e0c))
- Update Django example ([commit](https://github.com/miguelgrinberg/python-socketio/commit/dc7ac74c1d2c97544056541736d644060837a080))
- Documentation fix for async client ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5b9134617759a1b64adb2f9aba0974c732576cc4))
- Update documentation of asyncio server ([commit](https://github.com/miguelgrinberg/python-socketio/commit/98f3cb4664ff10c0bb17826b11564644bed99fd6))
- Fix documentation typo [#948](https://github.com/miguelgrinberg/python-socketio/issues/948) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f888446b330146484325b568cdc2303c9b35c095)) (thanks **mostlycryptic**!)

**Release 5.6.0** - 2022-04-24

- Catch and log errors in pubsub listening thread [#889](https://github.com/miguelgrinberg/python-socketio/issues/889) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f2ae136dcd724d56353b783092c448d6e638635f))
- Use new asyncio support in redis package [#911](https://github.com/miguelgrinberg/python-socketio/issues/911) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0e7691b77605de00dedcbf87e415bb79fcd7f2aa))
- Add support for aiopiko version 7 and higher [#897](https://github.com/miguelgrinberg/python-socketio/issues/897) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b4b55e1fb5e9d837b3301b5b873d9a7fe2a12023)) (thanks **Dmitriy**!)
- Fixed documentation typo [#910](https://github.com/miguelgrinberg/python-socketio/issues/910) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/16243e7c5f95f73f1f17b6febbf23c6483c17c62)) (thanks **Omar Costa Hamido**!)
- Fix aiohttp example's background task [#881](https://github.com/miguelgrinberg/python-socketio/issues/881) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fb9648575ef5bd529579f854f141df52d9e000ed))
- Bump sanic from 0.8 to 20.12.6 in /examples/server/sanic [#875](https://github.com/miguelgrinberg/python-socketio/issues/875) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/342f2e3fe9a3f973a491326b19fa4f96705b9b7e)) (thanks **dependabot[bot]**!)
- Add application name to Sanic example [#892](https://github.com/miguelgrinberg/python-socketio/issues/892) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4d5e36d36f865bf0527cfeb486a4e7f917b28717)) (thanks **Florian Metzger-Noel**!)

**Release 5.5.2** - 2022-02-15

- Connect with an empty auth object instead of `None` [#861](https://github.com/miguelgrinberg/python-socketio/issues/861) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/1fb7a76575426dd58a5e9c0e01646302ccc96188))
- Fix indentation in the "Rooms" docs example. [#872](https://github.com/miguelgrinberg/python-socketio/issues/872) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3336181f9ce5fe737d675f8343f18a885c651ebd)) (thanks **Ezio Melotti**!)
- Remove 3.6 and pypy-3.6 builds, add 3.10 and pypy-3.8 ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ed5679a7cb01963b44a5004e1236b7e8b485aa0b))

**Release 5.5.1** - 2022-01-11

- Support multiple Kafka servers ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4ee3649514b98c50cc0bf70d3f269389da52772d)) (thanks **sparkingdark**!)
- Include example code in flake8 pass ([commit](https://github.com/miguelgrinberg/python-socketio/commit/273a4b0439c84560d403662d8eba4122c28ba0d8))

**Release 5.5.0** - 2021-11-14

- Option to disable the SIGINT handler in the client [#792](https://github.com/miguelgrinberg/python-socketio/issues/792) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ea84b9b1c714b02eaf1081f4e37fd130a3159d8c))
- Do not invoke reserved events on a catch-all handler [#814](https://github.com/miguelgrinberg/python-socketio/issues/814) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/34f34e53d650dde605f5f4a98d7a70936524a1b8))
- Use correct binary packet types in the msgpack packet encoder [#811](https://github.com/miguelgrinberg/python-socketio/issues/811) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/60735dd4c2fc87ed863d7dbf7de361500d963dd3))
- Add missing `call()` method to namespace classes [#800](https://github.com/miguelgrinberg/python-socketio/issues/800) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/32db48d12ceb44d7a02fd9f05047b47c7ed3f4a5))
- Add missing `to` argument to namespace `emit()` and `send()` methods [#810](https://github.com/miguelgrinberg/python-socketio/issues/810) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ed08a01e65635160923f3d6d5755df74d53274e1))
- Configure Redis pubsub to skip subscription messages ([commit](https://github.com/miguelgrinberg/python-socketio/commit/e8fff07b367929794e5e30cecbf252b72d307c16))
- Migrate async Redis client manager to aioredis 2 [#771](https://github.com/miguelgrinberg/python-socketio/issues/771) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f245191d86722244a2d3d0529d9f5ff15dfd817a)) (thanks **Sam Mosleh**!)
- Update Python supported versions in docs ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a54152f2466bad4869d9cfdad6be3a5547e0b6bc))
- Document how to get the connection state in the client [#799](https://github.com/miguelgrinberg/python-socketio/issues/799) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/47c5f45c765ae207f58ba2675f91eaf8c79f8500))
- Improved documentation of `start_background_task()` function ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4f5bf1e9898154aa1a9896a7016ba22bfb73cdf2))
- Improved documentation of `call()` method [#813](https://github.com/miguelgrinberg/python-socketio/issues/813) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8c2a6ac86972bf94acafe687d2e86bdf65119960))
- Fixed intermittent test failures [#572](https://github.com/miguelgrinberg/python-socketio/issues/572) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/db0565ada6c8891be3230bcc415e5465bd409c09))

**Release 5.4.1** - 2021-10-14

- Catch-all event handlers ([commit](https://github.com/miguelgrinberg/python-socketio/commit/28569d48ad74d5414a0d2a8f69d7540dbdddf066))
- Implement disconnect method for external processes [#684](https://github.com/miguelgrinberg/python-socketio/issues/684) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a830c9f7887df715227f4284f30e8d62680e58ce))

**Release 5.4.0** - 2021-08-02

- Support msgpack and custom packet serializers [#749](https://github.com/miguelgrinberg/python-socketio/issues/749) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/5159e84c49daaf2da0579bfc6ee954a9c738a076))
- Return error packet if client connects to an already connected namespace ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cb1b8ec74bee3b5247200a6fc6e3f6aab3a3f941))
- Handle CancelledError in async pubsub managers [#750](https://github.com/miguelgrinberg/python-socketio/issues/750) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a813bde0626c16fe693db74cbc2ea7c331a177d3))
- More robust handling of emit's "to" argument [#689](https://github.com/miguelgrinberg/python-socketio/issues/689) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2f0d8bbd8c4de43fe26e0f2edcd05aef3c8c71f9))
- Remove executable permissions from setup.py, which has no shebang [#748](https://github.com/miguelgrinberg/python-socketio/issues/748) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fb3ac958dfa2d3b04f8ec1b0221c3f4734c9f756)) (thanks **Ben Beasley**!)
- Improved project structure ([commit](https://github.com/miguelgrinberg/python-socketio/commit/98c7ac23f231b64cc8b8c51104b792d0cd5cf361))

**Release 5.3.0** - 2021-05-15

- Document WebSocket support for threading mode ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2f085b3338acc56a5c4625783d50ad53f5ad0c1a))
- Allow functions to be used for URL, headers and auth data in client connection [#588](https://github.com/miguelgrinberg/python-socketio/issues/588) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7d2e7f7eb3eb34860c2b28df1807a932ed632b54))
- Emit events to multiple rooms [#605](https://github.com/miguelgrinberg/python-socketio/issues/605) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2538df8bcf0e44881a7653cc684f985252c7fce0))
- More descriptive error when joining a room on a bad namespace [#650](https://github.com/miguelgrinberg/python-socketio/issues/650) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/66068d9e968942343c840609e6e062162256111b))
- Document the use of arguments in the `connect_error` handler [#554](https://github.com/miguelgrinberg/python-socketio/issues/554) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d5308504d304b1bd26398309d31d0ce5fbd76e74))
- Document that callbacks cannot be used in external processes [#1533](https://github.com/miguelgrinberg/Flask-SocketIO/issues/1533) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/703843b42b8fb7fb6a9d0152610e714e9c6fb75e))
- Improve `start_background_task()` example in the documentation [#647](https://github.com/miguelgrinberg/python-socketio/issues/647) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/ef4ae900c5245439921e706fa46008fe5ca102d6))
- Added Open Collective funding option ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6572ad683ac87981493f69307d5e01cb15a0dacb))
- Remove Python 2 from PyPI classifiers ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a37ab00b344e035adbdc532f2760c223db118c0f))

**Release 5.2.1** - 2021-04-18

- Fixed incorrect handling of dashes inside the JSON payload of a packet [#675](https://github.com/miguelgrinberg/python-socketio/issues/675) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f4e101079fdc49c673ab9433aca8346480cc9e4f))

**Release 5.2.0** - 2021-04-17

- Pass custom authentication data with client connection [#661](https://github.com/miguelgrinberg/python-socketio/issues/661) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a07eedf54e535843401cd8b280c1bb24de3dfd27))
- Configure the JSON decoder for safer parsing ([commit](https://github.com/miguelgrinberg/python-socketio/commit/81b0b849bd7329c7fef2f6a9491aeae279d7b6e5)) (thanks **Onno Kortmann**!)
- Made parsing of id field of Socket.IO packet faster and more robust ([commit](https://github.com/miguelgrinberg/python-socketio/commit/09cb411776b9035343d7349650bc4b84715f00fd)) (thanks **Onno Kortmann**!)
- Correct use of a trailing comma in Socket.IO packets with no id or data [#671](https://github.com/miguelgrinberg/python-socketio/issues/671) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8d1aeb2e401713758a0a2576d0d1ea8eaf14896e))
- Updated Socket.IO JavaScript client versions in documentation example ([commit](https://github.com/miguelgrinberg/python-socketio/commit/9ff8bf354110e860c73f3298278c8be6ba44cb64))

**Release 5.1.0** - 2021-03-10

- Added `wait` argument to client's connect method [#634](https://github.com/miguelgrinberg/python-socketio/issues/634) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4da6d74f56a58e68b0aef08212347097dd73cda9))
- Invoke the disconnect handler when the client initiates a disconnection [#594](https://github.com/miguelgrinberg/python-socketio/issues/594) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3349b024d59a78a6a7282257941b4623af72d7c9))
- Pass auth information sent by client to the connect handler ([commit](https://github.com/miguelgrinberg/python-socketio/commit/11b6f1a08d4840cc2f20a644bd9db7d5d95496bf))
- Catch all possible Redis errors [#635](https://github.com/miguelgrinberg/python-socketio/issues/635) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6f812ef8e4b86db8d15fcc9a4d79b721fe7ca068))
- Reset message queue sleep timer upon reconnect ([commit](https://github.com/miguelgrinberg/python-socketio/commit/54180987cd429c6d48c6fdad5c97b1ca894d2b09)) (thanks **Ed Serzo**!)
- Fixed bad event object used by asyncio client reconnect logic [#622](https://github.com/miguelgrinberg/python-socketio/issues/622) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/bff76c432c12e678cc1043d8b046bd4a2fe22c28))
- Adding missing example of async client implementation to documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f341abe88ec19b20cd115dd246dd4bc2b3ad61fe)) (thanks **manuel**!)
- Add scrolling to documentation sidebar [#610](https://github.com/miguelgrinberg/python-socketio/issues/610) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/eabcc4679bc283acdb9f87022ef1e0e82c48497e)) (thanks **Mohammed Abdul Raheem**!)
- Typo fix in documentation [#602](https://github.com/miguelgrinberg/python-socketio/issues/602) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b418af4c53619305c0b91a040e40fc7f3b907a74)) (thanks **Tim Gates**!)

**Release 5.0.4** - 2020-12-25

- Include error message and arguments in CONNECT_ERROR packet [#590](https://github.com/miguelgrinberg/python-socketio/issues/590) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/314971c8a0ba327acd12b0ecfef84f0a5dd63bed))
- Fix typos in the documentation [#599](https://github.com/miguelgrinberg/python-socketio/issues/599) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/c809774c3ec0921306e7274987076b3ce51a4e95)) (thanks **Arpit Jain**!)
- Updated connection options in the documentation [#597](https://github.com/miguelgrinberg/python-socketio/issues/597) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/251fee1763df168fd070b89d83f24698ba0b3bb8))

**Release 5.0.3** - 2020-12-14

- Correct handling of user session [#585](https://github.com/miguelgrinberg/python-socketio/issues/585) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a61d59c02aa08483f86bf45accf6620b69b06a41))
- Performace tuning ([commit](https://github.com/miguelgrinberg/python-socketio/commit/bcdf9bb009ef32dac156ea518c1b113c0773877c))
- Updated ASGI examples to latest release ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8c5b762d724c0cfc45f982ffc3303202985ab812))
- Updated Django example to latest release ([commit](https://github.com/miguelgrinberg/python-socketio/commit/94afcf643a66d85b64d76f4c219afe8881e8dbe6))

**Release 5.0.2** - 2020-12-12

- Return `environ`` dictionary for a client ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2e71c22c6db41b82d863b3189c122ea9f7916bf0))

**Release 5.0.1** - 2020-12-08

- Fix Engine.IO dependency version ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d2bb2b12e536036e34d94a1ad87e0d48a1a504a8))
- Conversion from Socket.IO sid to Engine.IO sid ([commit](https://github.com/miguelgrinberg/python-socketio/commit/805b33fa7d2e38be4ada60e382c989433fd5af03))

**Release 5.0.0** - 2020-12-07

- Update to match the JavaScript Socket.IO 3.x releases (Socket.IO v5 protocol revision)
    - v5 protocol: do not connect the default namespace unless requested explicitly ([commit](https://github.com/miguelgrinberg/python-socketio/commit/49822e6919d3de9d52f6dde32c7f04ad62d73990))
    - v5 protocol: handle per-namespace sids in base manager ([commit](https://github.com/miguelgrinberg/python-socketio/commit/308b0c8eeb71e1fead35d19088a3291a15ccd50a))
    - v5 protocol: rename ERROR packet to CONNECT_ERROR ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4940fc1e1e2ddc86c28cd3b626dad75d6845243f))
    - v5 protocol: use Engine.IO 4.x
- Remove unnecessary binary argument ([commit](https://github.com/miguelgrinberg/python-socketio/commit/9270a5bcf85785935520ef816d314a5e197ed227))
- Remove dependency on the six package ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f6eeedb767614fb68b41927c8fd620c95cafcc6c))
- Added version compatibility chart to README ([commit](https://github.com/miguelgrinberg/python-socketio/commit/342ca0bb9da8b9ea6c63aa3bd05a37903416d301))

**Release 4.6.1** - 2020-11-28

- Added troubleshooting section to the documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/48906071307d79df356379fe6e05a73b0c65d9d4))
- Document the use of tuples when emitting ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3ac3437af781d54a343b4430d1f3546c580677e3))
- Handle the case of not having a previous signal handler [#518](https://github.com/miguelgrinberg/python-socketio/issues/518) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8107216848672792e420b3254b5217e51bcd4b32)) (thanks **David Brooks**!)
- Simplify asserts in unit tests ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a4f9992d34a49350a853d9f1a0c3d63034785ab3))
- Fixed route path for tornado server [#494](https://github.com/miguelgrinberg/python-socketio/issues/494) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/4385057c34bb468b9741edcd918e926a17c9af7c)) (thanks **someApprentice**!)
- Use pytest as test runner ([commit](https://github.com/miguelgrinberg/python-socketio/commit/280d132d284699cc1ae641b1e41403ceab6c66f5))
- Move builds to GitHub actions ([commit](https://github.com/miguelgrinberg/python-socketio/commit/104d5dd97b207cf59f47f1c72b408ed4b1e6f770))
- Fixed typo in documentation [#524](https://github.com/miguelgrinberg/python-socketio/issues/524) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/1fbf95940cfceca13a2033fb3d455810a3b34e83)) (thanks **Fover**!)

**Release 4.6.0** - 2020-05-23

- Improved handling of rejected connections [#391](https://github.com/miguelgrinberg/python-socketio/issues/391) [#487](https://github.com/miguelgrinberg/python-socketio/issues/487) [#447](https://github.com/miguelgrinberg/python-socketio/issues/447) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8d08096dc442e817b5e4ce53321ccf196daafcd1))
- Fix multi-namespace disconnect logic [#456](https://github.com/miguelgrinberg/python-socketio/issues/456) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/76a9860abc11b5a18fa05e6a8fef815390642d09))
- `AsyncPubSubManager` does not await for `can_disconnect()` [#488](https://github.com/miguelgrinberg/python-socketio/issues/488) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b0518936b949f759f2be8da0cc7b9c30af440371)) (thanks **Andrei Neagu**!)
- Require a recipient in `call()` function in the server [#476](https://github.com/miguelgrinberg/python-socketio/issues/476) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/bbb9a7f0b630b6932960ae2545c62d6e5aee4f09)) (thanks **tt2468**!)
- ASGI startup and shutdown lifespan handlers [#468](https://github.com/miguelgrinberg/python-socketio/issues/468) Co-authored-by: avi <senavi@berkeley.edu> ([commit](https://github.com/miguelgrinberg/python-socketio/commit/87d51dd1e6cde94adf4f8fb23828e1537c4f1301)) (thanks **databasedav**!)
- Remove references to Python 2.7 in the documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/02a7ce32c00ed5e64b0fae62d2d5ef93f25367df))
- Fix server example in docstring [#449](https://github.com/miguelgrinberg/python-socketio/issues/449) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8caebfd524d77d118243878c4bd9d396c420e0a3)) (thanks **wangjiancn**!)
- Fix documentation typo [#450](https://github.com/miguelgrinberg/python-socketio/issues/450) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/cdde846e575c98d1316b1857b933bfeabf159580)) (thanks **kizError**!)

**Release 4.5.1** - 2020-03-22

- Fix endless loop when disconnecting on multi-server deployments [#441](https://github.com/miguelgrinberg/python-socketio/issues/441) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/16e873dbc7e100780c83a907a11299bd8269e5e3))

**Release 4.5.0** - 2020-03-14

- Add support for client disconnects in multi-server configurations [#1174](https://github.com/miguelgrinberg/Flask-SocketIO/issues/1174) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/01378ef1efca73330327006be467270462d504e0))
- Initialize the client's SIGINT signal handler only if a client is created [#424](https://github.com/miguelgrinberg/python-socketio/issues/424) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/dc89963e328920a3756cefb508213c310ffa730c))
- Fix for `Server` and `AsyncServer` when emitting no data [#420](https://github.com/miguelgrinberg/python-socketio/issues/420) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/e2242ce40e65c682e031d245db50fdd7956c3b2d)) (thanks **Aaron**!)
- More accurate logging documentation ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d745477abf606f56f566f9d5b1b7bf9ffdb4fbc6))
- `AsyncClient` documentation fixes [#389](https://github.com/miguelgrinberg/python-socketio/issues/389) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/aa2882cb3e2f3cda3a9d8c94b1c5db1bd0dbbf99)) (thanks **Dmitry Volodin**!)
- Document concurrency problems with emits [#403](https://github.com/miguelgrinberg/python-socketio/issues/403) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d972ca3a5476f5e4e9a114913bdd5f528e558a9f))
- Minor documentation fixes [#386](https://github.com/miguelgrinberg/python-socketio/issues/386) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d4b403431152cbbbf31ff723562b069a36c330c4)) (thanks **Rotzbua**!)

**Release 4.4.0** - 2019-11-24

- Last version to support Python 2
- Support the `connect_error` event in the client [#344](https://github.com/miguelgrinberg/python-socketio/issues/344) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/805d5f37413a1e3bbad22012237412803217b4b9))
- Do not dispatch events for disconnected namespaces [#333](https://github.com/miguelgrinberg/python-socketio/issues/333) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/a839a36fa0fa7f0e5d8976ff47b217f6b1e8a44b))
- Fix documentation typos [#374](https://github.com/miguelgrinberg/python-socketio/issues/374) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b60bbc0307edd0bef2c8b11197ef5a04b2d11b71)) (thanks **Dmitry Volodin**!)
- Updated documentation with new Engine.IO client options ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7c32b379aeeafdb4d6e24e8695734c985753a9d7))

**Release 4.3.1** - 2019-08-05

- New asyncio based RabbitMQ manager [#320](https://github.com/miguelgrinberg/python-socketio/issues/320) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d984f32e76cc3c204fb6099cbb3c3cd91bfe6e3a)) (thanks **salimaboubacar**!)
- New Apache Kafka manager ([commit](https://github.com/miguelgrinberg/python-socketio/commit/36d17856f43c6ce750e6318e8994b4e2426f480a))
- Pass additional options to Redis and Kombu managers [#307](https://github.com/miguelgrinberg/python-socketio/issues/307) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7dbc47049a605f78d795b6f59d458522d67c6fe6))
- Do not allow emits on a namespace that is not connected [#325](https://github.com/miguelgrinberg/python-socketio/issues/325) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f2c1cf7f04cefa57182eeb646c4f3fe246e69b0c))
- Disconnect Engine.IO connection when server disconnects a client [#1017](https://github.com/miguelgrinberg/Flask-SocketIO/issues/1017) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/516a2958f4e87041aeeea0a0a8e3622d3d636184))
- Update CORS documentation [#327](https://github.com/miguelgrinberg/python-socketio/issues/327) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/6848bed1d74219eeb7f2ead40a77e775f48c68ee))
- Updated documentation on message queue manager classes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/f36fa88d9e4cba33e1c008b5535448326ea3a461))
- Documentation fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d23581e657413043afa378d7be6020940ebf4af8))

**Release 4.3.0** - 2019-07-29

- Address potential websocket cross-origin attacks [#128](https://github.com/miguelgrinberg/python-engineio/issues/128) ([commit](https://github.com/miguelgrinberg/python-engineio/commit/7548f704a0a3000b7ac8a6c88796c4ae58aa9c37))
- Documentation for the Same Origin security policy ([commit](https://github.com/miguelgrinberg/python-socketio/commit/045188c63dffeec82539354fd0498fca969e444e))

**Release 4.2.1** - 2019-07-27

- Added rediss:// URL scheme to AsyncRedisManager [#319](https://github.com/miguelgrinberg/python-socketio/issues/319) * Added rediss:// URL scheme to AsyncRedisManager * Obeyed flake8 ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0b25ff42b8927ac881be7c8ebe1785819bc4c35e)) (thanks **Dylan Anthony**!)

**Release 4.2.0** - 2019-06-29

- Handle keyboard interrupt during reconnect [#301](https://github.com/miguelgrinberg/python-socketio/issues/301) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/fa53e3869ce27af3d497d6e021aa2e3d5c808ece))
- Added "to" parameter as an alias to "room" ([commit](https://github.com/miguelgrinberg/python-socketio/commit/8a4e5ffa5ceb03b63156b9520e79a4c7414ac214))
- Correctly autodetect asgi async mode ([commit](https://github.com/miguelgrinberg/python-socketio/commit/eecd3676c15bb7c4c0e165eb02c814cba53a6bb4))
- Improved documentation on user session behavior on disconnections [#308](https://github.com/miguelgrinberg/python-socketio/issues/308) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/2aa8636223d714b1c87323f625645a433ac7e010))

**Release 4.1.0** - 2019-06-03

- New @event decorator for handler registration ([commit](https://github.com/miguelgrinberg/python-socketio/commit/70ebfdbfa1ad40e471b93dc9b0d3a9c2e7025ce0))
- Much more flexible support for static files in the server ([commit](https://github.com/miguelgrinberg/python-socketio/commit/aaa87a82779c5dbd5f2cac19991a6ca93bde90ae))
- Move python-engineio dependency to versions 3.8 and up ([commit](https://github.com/miguelgrinberg/python-socketio/commit/814ff84ec310ce208522c8fd00302fdc1a689f44))
- Various simplifications to examples ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0f42c181da7c56ca270814442bdebeecb0e38bf6))
- Expose the sid for the connection as `sio.sid` ([commit](https://github.com/miguelgrinberg/python-socketio/commit/3b32dbde8d59d0df7c958534732f5d5437f8decf))

**Release 4.0.3** - 2019-05-25

- skip_sid parameter can also be a list [#202](https://github.com/miguelgrinberg/python-socketio/issues/202) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/00d39ca6985e94e283f5c766c18cacb760e0658d))
- Fixed Sanic documentation [#193](https://github.com/miguelgrinberg/python-socketio/issues/193) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/0249f05a2fb94c29f3be5cb33248b30d6c748eba))
- Added note on CORS support for sanic [#205](https://github.com/miguelgrinberg/python-socketio/issues/205) ([commit](https://github.com/miguelgrinberg/python-socketio/commit/d3e19b7e52debe0db759f56e25eb2706ad2434b6))
- flake8 fixes ([commit](https://github.com/miguelgrinberg/python-socketio/commit/18fa5286c7505813aca2a8c99606bdcce7cadf31))
- added python 3.7 build ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7348d923e3af0331706c51053120e672fa0dabc1))
- added change log ([commit](https://github.com/miguelgrinberg/python-socketio/commit/7803a7bce0fca52f8b40668e97395018be339c16))
- auto-generate change log during release ([commit](https://github.com/miguelgrinberg/python-socketio/commit/b46dc0fa1a1435dcbd43d21b2c6d0bc33a4da6ea))

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
