/*Application Package Name: org.fdroid.fdroid
class PRCS_28 {
/**
com.google.zxing.client.android.AmbientLightManager;start()V
*/

    public void start()
    {
        if (this.cameraSettings.isAutoTorchEnabled()) {
            android.hardware.SensorManager v0_4 = ((android.hardware.SensorManager) this.context.getSystemService("sensor"));
            android.hardware.Sensor v1_0 = v0_4.getDefaultSensor(5);
            this.lightSensor = v1_0;
            if (v1_0 != null) {
                v0_4.registerListener(this, v1_0, 3);
            }
        }
        return;
    }

/**
com.journeyapps.barcodescanner.camera.CameraManager;startPreview()V
*/

    public void startPreview()
    {
        com.google.zxing.client.android.AmbientLightManager v0_0 = this.camera;
        if ((v0_0 != null) && (!this.previewing)) {
            v0_0.startPreview();
            this.previewing = 1;
            this.autoFocusManager = new com.journeyapps.barcodescanner.camera.AutoFocusManager(this.camera, this.settings);
            com.google.zxing.client.android.AmbientLightManager v0_3 = new com.google.zxing.client.android.AmbientLightManager(this.context, this, this.settings);
            this.ambientLightManager = v0_3;
            v0_3.start();
        }
        return;
    }

/**
com.journeyapps.barcodescanner.camera.CameraInstance;run()V
*/

    public void run()
    {
        try {
            android.util.Log.d(com.journeyapps.barcodescanner.camera.CameraInstance.access$000(), "Starting preview");
            com.journeyapps.barcodescanner.camera.CameraInstance.access$100(this.this$0).setPreviewDisplay(com.journeyapps.barcodescanner.camera.CameraInstance.access$500(this.this$0));
            com.journeyapps.barcodescanner.camera.CameraInstance.access$100(this.this$0).startPreview();
        } catch (Exception v0_3) {
            com.journeyapps.barcodescanner.camera.CameraInstance.access$200(this.this$0, v0_3);
            android.util.Log.e(com.journeyapps.barcodescanner.camera.CameraInstance.access$000(), "Failed to start preview", v0_3);
        }
        return;
    }


}