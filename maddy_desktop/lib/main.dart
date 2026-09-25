import 'dart:io';
import 'dart:convert';
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:hotkey_manager/hotkey_manager.dart';
import 'package:flutter/foundation.dart';

void main() {
  runApp(const MaddyApp());
}

class MaddyApp extends StatelessWidget {
  const MaddyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Maddy AI',
      theme: ThemeData.dark(),
      home: const MaddyHome(),
    );
  }
}

class MaddyHome extends StatefulWidget {
  const MaddyHome({super.key});

  @override
  State<MaddyHome> createState() => _MaddyHomeState();
}

class _MaddyHomeState extends State<MaddyHome>
    with SingleTickerProviderStateMixin {
  bool isRunning = false;
  Process? maddyProcess;

  String maddyStatus = 'Ready when you are.';
  bool isStartHovered = false;
  bool isStopHovered = false;

  int cpuUsage = 0;
  int ramUsage = 0;
  int storageUsage = 0;
  int batteryUsage = 0;

  Timer? systemInfoTimer;
  HotKey? maddyHotKey;

  // =========================================================
  // FIND PYTHON / MADDY DIRECTORY
  // =========================================================

  String getPythonDirectory() {
    final exeDirectory = File(Platform.resolvedExecutable).parent.path;

    // Final installed/release version:
    // MaddyRelease/
    //   maddy_desktop.exe
    //   python/
    //      MaddyPython.exe
    //      SystemInfoRunner.exe

    final bundledDirectory = '$exeDirectory\\python';

    if (File('$bundledDirectory\\MaddyPython.exe').existsSync()) {
      return bundledDirectory;
    }

    // Development fallback
    return r'F:\maddy\maddyassistant\dist';
  }

  String getMaddyPythonPath() {
    return '${getPythonDirectory()}\\MaddyPython.exe';
  }

  String getSystemInfoPath() {
    return '${getPythonDirectory()}\\SystemInfoRunner.exe';
  }

  // =========================================================
  // SYSTEM INFORMATION
  // =========================================================

  Future<void> getSystemInfo() async {
    try {
      final systemInfoPath = getSystemInfoPath();
      final pythonDirectory = getPythonDirectory();

      debugPrint('----------------------------------------');
      debugPrint('SystemInfo path: $systemInfoPath');
      debugPrint('SystemInfo exists: ${File(systemInfoPath).existsSync()}');
      debugPrint('Working directory: $pythonDirectory');

      final result = await Process.run(
        systemInfoPath,
        [],
        workingDirectory: pythonDirectory,
        runInShell: false,
      );

      debugPrint('SystemInfo exit code: ${result.exitCode}');
      debugPrint('SystemInfo stdout: ${result.stdout}');
      debugPrint('SystemInfo stderr: ${result.stderr}');

      if (result.exitCode == 0) {
        final lines = result.stdout.toString().trim().split(RegExp(r'\r?\n'));

        if (lines.length >= 4) {
          final cpu = int.tryParse(lines[0].trim());
          final ram = int.tryParse(lines[1].trim());
          final storage = int.tryParse(lines[2].trim());
          final battery = int.tryParse(lines[3].trim());

          if (cpu != null &&
              ram != null &&
              storage != null &&
              battery != null &&
              mounted) {
            setState(() {
              cpuUsage = cpu;
              ramUsage = ram;
              storageUsage = storage;
              batteryUsage = battery;
            });
          }
        }
      }
    } catch (e) {
      debugPrint('SYSTEM INFO ERROR: $e');
    }
  }

  // =========================================================
  // ANIMATION
  // =========================================================

  late AnimationController animationController;

  // =========================================================
  // INIT
  // =========================================================

  @override
  void initState() {
    super.initState();

    getSystemInfo();

    systemInfoTimer = Timer.periodic(
      const Duration(seconds: 3),
      (_) => getSystemInfo(),
    );

    animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  // =========================================================
  // DISPOSE
  // =========================================================

  @override
  void dispose() {
    systemInfoTimer?.cancel();
    maddyProcess?.kill();
    animationController.dispose();
    super.dispose();
  }

  // =========================================================
  // START MADDY
  // =========================================================

  Future<void> startMaddy() async {
    if (maddyProcess != null) {
      return;
    }

    try {
      final maddyPath = getMaddyPythonPath();
      final pythonDirectory = getPythonDirectory();

      debugPrint('========================================');
      debugPrint('Starting Maddy...');
      debugPrint('Maddy path: $maddyPath');
      debugPrint('Maddy exists: ${File(maddyPath).existsSync()}');
      debugPrint('Working directory: $pythonDirectory');

      final process = await Process.start(
        maddyPath,
        [],
        workingDirectory: pythonDirectory,
        runInShell: false,
      );

      maddyProcess = process;

      debugPrint('Maddy started. PID: ${process.pid}');

      if (!mounted) return;

      setState(() {
        isRunning = true;
        maddyStatus = 'Maddy is listening...';
      });

      process.stdout.transform(utf8.decoder).listen((data) {
        debugPrint('MADDY OUTPUT: $data');
      });

      process.stderr.transform(utf8.decoder).listen((data) {
        debugPrint('MADDY ERROR: $data');
      });

      process.exitCode.then((exitCode) {
        debugPrint('Maddy exited with code: $exitCode');

        if (!mounted) return;

        setState(() {
          isRunning = false;
          maddyProcess = null;
          maddyStatus = 'Ready when you are.';
        });
      });
    } catch (e) {
      debugPrint('MADDY START ERROR: $e');

      if (!mounted) return;

      setState(() {
        isRunning = false;
        maddyProcess = null;
        maddyStatus = 'Could not start Maddy.';
      });
    }
  }

  // =========================================================
  // STOP MADDY
  // =========================================================

  Future<void> stopMaddy() async {
    final process = maddyProcess;

    if (process == null) {
      return;
    }

    try {
      if (Platform.isWindows) {
        await Process.run('taskkill', [
          '/F',
          '/T',
          '/PID',
          process.pid.toString(),
        ], runInShell: true);
      } else {
        process.kill();
      }
    } catch (e) {
      debugPrint('Could not stop Maddy: $e');
    }

    if (!mounted) return;

    setState(() {
      isRunning = false;
      maddyProcess = null;
      maddyStatus = 'Ready when you are.';
    });
  }

  // =========================================================
  // VOICE WAVE
  // =========================================================

  Widget buildVoiceWave() {
    return AnimatedBuilder(
      animation: animationController,
      builder: (context, child) {
        final value = animationController.value;

        return Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: List.generate(5, (index) {
            final waveHeight = isRunning
                ? 8 + ((value + index * 0.15) % 1) * 20
                : 6.0;

            return AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              margin: const EdgeInsets.symmetric(horizontal: 2),
              width: 3,
              height: waveHeight,
              decoration: BoxDecoration(
                color: isRunning ? Colors.cyanAccent : Colors.white24,
                borderRadius: BorderRadius.circular(5),
                boxShadow: isRunning
                    ? [
                        BoxShadow(
                          color: Colors.cyanAccent.withOpacity(0.5),
                          blurRadius: 8,
                        ),
                      ]
                    : [],
              ),
            );
          }),
        );
      },
    );
  }

  // =========================================================
  // SYSTEM INFO ITEM
  // =========================================================

  Widget _systemInfoItem(String title, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          title,
          style: const TextStyle(
            color: Colors.white54,
            fontSize: 10,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(width: 5),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  // =========================================================
  // BUILD
  // =========================================================

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    final horizontalPadding = screenWidth * 0.04;

    final robotSize = screenHeight * 0.36;
    final safeRobotSize = robotSize.clamp(180.0, 300.0);

    final imageSize = safeRobotSize * 0.63;

    final titleSize = screenWidth * 0.025;
    final descriptionSize = screenWidth * 0.011;

    final verticalGapSmall = screenHeight * 0.015;
    final verticalGapLarge = screenHeight * 0.04;

    return Scaffold(
      backgroundColor: const Color(0xFF050914),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment.center,
            radius: 1.2,
            colors: [Color(0xFF101D38), Color(0xFF050914)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: horizontalPadding,
              vertical: screenHeight * 0.025,
            ),
            child: Column(
              children: [
                // =====================================================
                // TOP BAR
                // =====================================================
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '✦ MADDY',
                      style: TextStyle(
                        fontSize: (screenWidth * 0.018).clamp(20.0, 28.0),
                        fontWeight: FontWeight.bold,
                        letterSpacing: 5,
                      ),
                    ),

                    Row(
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 400),
                          width: 11,
                          height: 11,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: isRunning
                                ? Colors.cyanAccent
                                : Colors.redAccent,
                            boxShadow: [
                              BoxShadow(
                                color: isRunning
                                    ? Colors.cyanAccent
                                    : Colors.redAccent,
                                blurRadius: 15,
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(width: 10),

                        Text(
                          isRunning ? 'ONLINE' : 'OFFLINE',
                          style: TextStyle(
                            color: isRunning
                                ? Colors.cyanAccent
                                : Colors.redAccent,
                            letterSpacing: 3,
                            fontWeight: FontWeight.bold,
                            fontSize: (screenWidth * 0.009).clamp(11.0, 15.0),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),

                SizedBox(height: verticalGapLarge),

                // =====================================================
                // ROBOT
                // =====================================================
                Flexible(
                  flex: 5,
                  child: AnimatedBuilder(
                    animation: animationController,
                    builder: (context, child) {
                      final glow = isRunning
                          ? 25 + (animationController.value * 40)
                          : 20 + (animationController.value * 15);

                      final ringSize =
                          safeRobotSize +
                          (isRunning
                              ? animationController.value * 35
                              : animationController.value * 10);

                      return Center(
                        child: SizedBox(
                          width: ringSize + 30,
                          height: ringSize + 30,
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              if (isRunning)
                                Container(
                                  width: ringSize,
                                  height: ringSize,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: Colors.cyanAccent.withOpacity(
                                        0.25 + animationController.value * 0.35,
                                      ),
                                      width: 2,
                                    ),
                                  ),
                                ),

                              Container(
                                width: safeRobotSize,
                                height: safeRobotSize,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  gradient: const RadialGradient(
                                    colors: [
                                      Color(0xFF1B8FFF),
                                      Color(0xFF0A2A55),
                                      Colors.transparent,
                                    ],
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.cyanAccent.withOpacity(
                                        isRunning ? 0.35 : 0.25,
                                      ),
                                      blurRadius: glow,
                                      spreadRadius: 8,
                                    ),
                                  ],
                                ),
                                child: Center(
                                  child: Container(
                                    width: imageSize,
                                    height: imageSize,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: Colors.cyanAccent.withOpacity(
                                          0.5,
                                        ),
                                        width: 2,
                                      ),
                                      color: const Color(0xFF081326),
                                    ),
                                    child: ClipOval(
                                      child: Image.asset(
                                        'assets/images/robots.png',
                                        fit: BoxFit.cover,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),

                SizedBox(height: verticalGapSmall),

                // =====================================================
                // MADDY NAME
                // =====================================================
                Text(
                  'MADDY',
                  style: TextStyle(
                    fontSize: titleSize.clamp(28.0, 40.0),
                    fontWeight: FontWeight.bold,
                    letterSpacing: 10,
                  ),
                ),

                SizedBox(height: verticalGapSmall),

                // =====================================================
                // DESCRIPTION
                // =====================================================
                AnimatedContainer(
                  duration: const Duration(milliseconds: 400),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.04),
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(
                      color: isRunning
                          ? Colors.cyanAccent.withOpacity(0.35)
                          : Colors.white.withOpacity(0.08),
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        isRunning ? Icons.graphic_eq : Icons.auto_awesome,
                        size: 17,
                        color: isRunning ? Colors.cyanAccent : Colors.white54,
                      ),

                      const SizedBox(width: 10),

                      Text(
                        maddyStatus,
                        style: TextStyle(
                          fontSize: descriptionSize.clamp(13.0, 17.0),
                          color: isRunning ? Colors.cyanAccent : Colors.white60,
                          letterSpacing: 0.8,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 25),

                // =====================================================
                // SYSTEM STATUS
                // =====================================================
                if (!kIsWeb)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.white24),
                      color: Colors.white.withOpacity(0.05),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Center(
                          child: Text(
                            'SYSTEM STATUS',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 2,
                            ),
                          ),
                        ),

                        const SizedBox(height: 10),

                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            _systemInfoItem('CPU', '$cpuUsage%'),
                            _systemInfoItem('RAM', '$ramUsage%'),
                            _systemInfoItem('STORAGE', '$storageUsage%'),
                            _systemInfoItem('BATTERY', '$batteryUsage%'),
                          ],
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: 30),

                // =====================================================
                // BUTTONS
                // =====================================================
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    MouseRegion(
                      cursor: isRunning
                          ? SystemMouseCursors.basic
                          : SystemMouseCursors.click,
                      onEnter: (_) {
                        setState(() {
                          isStartHovered = true;
                        });
                      },
                      onExit: (_) {
                        setState(() {
                          isStartHovered = false;
                        });
                      },
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(14),
                          boxShadow: isRunning || !isStartHovered
                              ? []
                              : [
                                  BoxShadow(
                                    color: Colors.cyanAccent.withOpacity(0.45),
                                    blurRadius: 25,
                                    spreadRadius: 2,
                                  ),
                                ],
                        ),
                        child: ElevatedButton.icon(
                          onPressed: isRunning ? null : startMaddy,
                          icon: const Icon(Icons.play_arrow),
                          label: const Text(
                            'START',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              letterSpacing: 2,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.cyanAccent,
                            foregroundColor: Colors.black,
                            disabledBackgroundColor: Colors.cyanAccent
                                .withOpacity(0.25),
                            disabledForegroundColor: Colors.white38,
                            padding: EdgeInsets.symmetric(
                              horizontal: screenWidth * 0.035,
                              vertical: screenHeight * 0.018,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                        ),
                      ),
                    ),

                    SizedBox(width: screenWidth * 0.02),

                    MouseRegion(
                      cursor: !isRunning
                          ? SystemMouseCursors.basic
                          : SystemMouseCursors.click,
                      onEnter: (_) {
                        setState(() {
                          isStopHovered = true;
                        });
                      },
                      onExit: (_) {
                        setState(() {
                          isStopHovered = false;
                        });
                      },
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(14),
                          boxShadow: !isRunning || !isStopHovered
                              ? []
                              : [
                                  BoxShadow(
                                    color: Colors.redAccent.withOpacity(0.45),
                                    blurRadius: 25,
                                    spreadRadius: 2,
                                  ),
                                ],
                        ),
                        child: ElevatedButton.icon(
                          onPressed: isRunning ? stopMaddy : null,
                          icon: const Icon(Icons.stop),
                          label: const Text(
                            'STOP',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              letterSpacing: 2,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF1A2233),
                            foregroundColor: Colors.white,
                            disabledBackgroundColor: const Color(0xFF111722),
                            disabledForegroundColor: Colors.white24,
                            padding: EdgeInsets.symmetric(
                              horizontal: screenWidth * 0.035,
                              vertical: screenHeight * 0.018,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: verticalGapSmall),

                // =====================================================
                // MICROPHONE
                // =====================================================
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.mic,
                      size: 17,
                      color: isRunning ? Colors.cyanAccent : Colors.white38,
                    ),

                    const SizedBox(width: 10),

                    buildVoiceWave(),

                    const SizedBox(width: 12),

                    Text(
                      isRunning ? 'LISTENING' : 'MICROPHONE OFF',
                      style: TextStyle(
                        fontSize: (screenWidth * 0.009).clamp(11.0, 15.0),
                        color: isRunning ? Colors.cyanAccent : Colors.white38,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ],
                ),

                const Spacer(),

                // =====================================================
                // FOOTER
                // =====================================================
                Text(
                  'MADDY AI • DESKTOP ASSISTANT',
                  style: TextStyle(
                    fontSize: (screenWidth * 0.006).clamp(9.0, 12.0),
                    color: Colors.white24,
                    letterSpacing: 3,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
