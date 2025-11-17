import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:dio/dio.dart';
import 'dart:io';

// Configuración de la API (cambiar según URL local/AWS)
const String API_BASE_URL = "http://localhost:8000/api";

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Traductor de Lengua de Señas',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

// ==================== HOME SCREEN ====================
class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Traductor de Lengua de Señas'),
        elevation: 0,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.sign_language,
              size: 80,
              color: Colors.blue[400],
            ),
            const SizedBox(height: 32),
            const Text(
              'Bienvenido',
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text(
              'Graba tus señas y obten la traducción',
              style: TextStyle(fontSize: 16, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const CameraScreen()),
                );
              },
              icon: const Icon(Icons.videocam),
              label: const Text('Grabar Seña'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                backgroundColor: Colors.blue,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ==================== CAMERA SCREEN ====================
class CameraScreen extends StatefulWidget {
  const CameraScreen({Key? key}) : super(key: key);

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  bool _isRecording = false;
  List<CameraDescription>? _cameras;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras!.isNotEmpty) {
        _controller = CameraController(
          _cameras![0], // Cámara frontal
          ResolutionPreset.high,
        );
        await _controller!.initialize();
        setState(() {});
      }
    } catch (e) {
      print('Error inicializando cámara: $e');
    }
  }

  Future<void> _startRecording() async {
    if (!_controller!.value.isInitialized) return;

    try {
      await _controller!.startVideoRecording();
      setState(() => _isRecording = true);
    } catch (e) {
      print('Error grabando: $e');
    }
  }

  Future<void> _stopRecording() async {
    if (!_controller!.value.isRecordingVideo) return;

    try {
      final video = await _controller!.stopVideoRecording();
      setState(() => _isRecording = false);

      // Ir a pantalla de resultados
      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultsScreen(videoPath: video.path),
          ),
        );
      }
    } catch (e) {
      print('Error deteniendo grabación: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null || !_controller!.value.isInitialized) {
      return Scaffold(
        appBar: AppBar(title: const Text('Cámara')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Graba tu Seña'),
      ),
      body: Stack(
        children: [
          CameraPreview(_controller!),
          Positioned(
            bottom: 32,
            left: 0,
            right: 0,
            child: Center(
              child: FloatingActionButton(
                onPressed: _isRecording ? _stopRecording : _startRecording,
                backgroundColor: _isRecording ? Colors.red : Colors.green,
                child: Icon(_isRecording ? Icons.stop : Icons.circle),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
}

// ==================== RESULTS SCREEN ====================
class ResultsScreen extends StatefulWidget {
  final String videoPath;

  const ResultsScreen({Key? key, required this.videoPath}) : super(key: key);

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  late Dio _dio;
  String? _jobId;
  bool _isProcessing = false;
  String? _gloss;
  String? _translation;
  String? _error;

  @override
  void initState() {
    super.initState();
    _dio = Dio(BaseOptions(baseUrl: API_BASE_URL));
    _uploadAndProcessVideo();
  }

  Future<void> _uploadAndProcessVideo() async {
    try {
      setState(() => _isProcessing = true);

      // Paso 1: Upload video
      FormData formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          widget.videoPath,
          filename: 'video.mp4',
        ),
      });

      final uploadResponse = await _dio.post(
        '/upload-video',
        data: formData,
      );

      _jobId = uploadResponse.data['job_id'];
      print('Video uploaded with job_id: $_jobId');

      // Paso 2: Trigger processing
      await _dio.post('/process-video/$_jobId');
      print('Processing started');

      // Paso 3: Poll for results
      await _pollForResults();
    } catch (e) {
      setState(() => _error = 'Error: $e');
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _pollForResults() async {
    int maxAttempts = 120; // 2 minutos máximo
    int attempts = 0;

    while (attempts < maxAttempts) {
      try {
        final statusResponse = await _dio.get('/status/$_jobId');
        final status = statusResponse.data['status'];

        if (status == 'completed') {
          final resultResponse = await _dio.get('/result/$_jobId');
          setState(() {
            _gloss = resultResponse.data['gloss'];
            _translation = resultResponse.data['translation'];
          });
          return;
        } else if (status == 'error') {
          setState(
              () => _error = resultResponse.data.get('error', 'Error desconocido'));
          return;
        }

        // Esperar 1 segundo antes de intentar de nuevo
        await Future.delayed(const Duration(seconds: 1));
        attempts++;
      } catch (e) {
        print('Error polling: $e');
        await Future.delayed(const Duration(seconds: 1));
        attempts++;
      }
    }

    setState(() => _error = 'Timeout: Procesamiento tardó demasiado');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Resultado de la Traducción'),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              if (_isProcessing)
                const Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Procesando video...'),
                  ],
                )
              else if (_error != null)
                Column(
                  children: [
                    const Icon(Icons.error, color: Colors.red, size: 48),
                    const SizedBox(height: 16),
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                  ],
                )
              else if (_gloss != null && _translation != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Glosa Identificada:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(_gloss!),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Traducción al Español:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.blue[50],
                        border: Border.all(color: Colors.blue),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _translation!,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.pop(context);
                },
                child: const Text('Grabar Otra Seña'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
