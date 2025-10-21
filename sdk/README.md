# VoiceStudio Plugin SDK (gRPC over localhost)

Implement a small gRPC server exposing:

- ListPlugins() -> descriptors
- Run(op, jsonOptions, inPaths, outDir) -> result

Categories: voice-adapter, dsp-filter, exporter, analyzer

The UI discovers on port range 59110-59130 and lists plugins with icons.

## Proto sketch

```proto
syntax = "proto3";
package voicestudio.plugins.v1;

message Empty {}

message PluginDescriptor {
  string id = 1;
  string name = 2;
  string category = 3; // voice-adapter | dsp-filter | exporter | analyzer
  string icon = 4;     // data URL or path
}

message ListReply { repeated PluginDescriptor items = 1; }

message RunRequest {
  string op = 1;          // operation name
  string json_options = 2; // JSON string of options
  repeated string in_paths = 3;
  string out_dir = 4;
}

message RunReply {
  string status = 1; // ok | error
  string message = 2;
  repeated string outputs = 3;
}

service PluginHost {
  rpc ListPlugins(Empty) returns (ListReply);
  rpc Run(RunRequest) returns (RunReply);
}
```

## Sample

See `samples/null` for a minimal analyzer that emits RMS/peak stats.
