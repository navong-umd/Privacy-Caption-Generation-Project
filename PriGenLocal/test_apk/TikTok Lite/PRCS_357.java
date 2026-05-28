/*Application Package Name: com.tiktok.lite.go
class PRCS_357 {
/**
X.17v;L(LX/272; LX/17w;)V
*/

    public static final void L(X.272 p21, X.17w p22)
    {
        p21.LCC = p22;
        try {
            android.hardware.Sensor v8_0;
            android.hardware.SensorManager v1 = p21.LFFFF();
            X.17w v0_1 = p21.LCC;
            android.hardware.SensorManager v12 = p21.LFFFF();
            com.bytedance.helios.statichook.api.HeliosApiHook v7_0 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v13 = new Object[1];
            v13[0] = Integer.valueOf(1);
            com.bytedance.helios.statichook.api.ExtraInfo v14_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", "dzBzEgAjS8/YVFkiQFyNY/5YsGxLrjrnefn6WvofFe5V4G8pD2FouL38wJ9kJLN/fA9lNKgE3gpdwq5KTNjMve5smkw3/PaPzS7YyNO4z6rm");
            com.bytedance.helios.statichook.api.Result v4_1 = v7_0.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, "android.hardware.Sensor", v14_1);
        } catch (Exception) {
            return;
        }
        if (!v4_1.intercept) {
            v8_0 = v12.getDefaultSensor(1);
            v7_0.postInvoke(v8_0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, v14_1, 1);
        } else {
            v7_0.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, v14_1, 0);
            v8_0 = ((android.hardware.Sensor) v4_1.returnValue);
        }
        X.0a3.L(v1, v0_1, v8_0, 2, p21.LFFL().registerSensor());
        return;
    }

/**
X.272;L(LX/18L;)V
*/

    public final void L(X.18L p3)
    {
        X.17v.L(this, new X.17w(p3, new X.2hS(this)));
        return;
    }


}