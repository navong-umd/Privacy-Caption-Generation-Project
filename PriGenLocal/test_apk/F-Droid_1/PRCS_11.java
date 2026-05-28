/* Application Package Name: org.fdroid.fdroid */
class PRCS_11 {
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


}
