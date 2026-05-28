/*Application Package Name: com.tiktok.lite.go
class PRCS_361 {
/**
ms.bd.o.e2;L(Landroid/hardware/SensorManager; I Ljava/lang/String;)Landroid/hardware/Sensor;
*/

    public static android.hardware.Sensor L(android.hardware.SensorManager p17, int p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v10 = new Object[1];
        v10[0] = Integer.valueOf(p18);
        com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v4_1.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", p17, v10, "android.hardware.Sensor", v11_1);
        if (!v1_0.intercept) {
            android.hardware.Sensor v5_0 = p17.getDefaultSensor(p18);
            v4_1.postInvoke(v5_0, 100703, "android/hardware/SensorManager", "getDefaultSensor", p17, v10, v11_1, 1);
            return v5_0;
        } else {
            v4_1.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", p17, v10, v11_1, 0);
            return ((android.hardware.Sensor) v1_0.returnValue);
        }
    }

/**
ms.bd.o.e2;L()V
*/

    public final declared_synchronized void L()
    {
        try {
            if (!this.LFF) {
                String v0_10 = new android.os.HandlerThread("sensorThread");
                this.LF = v0_10;
                v0_10.start();
                this.LD = new com.bytedance.bpea.transmit.delegate.a(this.LF.getLooper());
                System.currentTimeMillis();
                try {
                    android.hardware.SensorManager v3_0 = this.LFFFF;
                } catch (String v0_17) {
                    throw v0_17;
                }
                if (v3_0 == null) {
                    this.LFF = 1;
                } else {
                    ms.bd.o.e2.L(v3_0, this, ms.bd.o.e2.L(v3_0, 10, "eSwwXgZ0UITZBw=="), this.LD, "eSwwXgZ0UITZBw==");
                    android.hardware.SensorManager v3_1 = this.LFFFF;
                    ms.bd.o.e2.L(v3_1, this, ms.bd.o.e2.L(v3_1, 9, "eSwwXgZ0UITZBw=="), this.LD, "eSwwXgZ0UITZBw==");
                    android.hardware.SensorManager v3_2 = this.LFFFF;
                    ms.bd.o.e2.L(v3_2, this, ms.bd.o.e2.L(v3_2, 4, "eSwwXgZ0UITZBw=="), this.LD, "eSwwXgZ0UITZBw==");
                    android.hardware.SensorManager v3_3 = this.LFFFF;
                    ms.bd.o.e2.L(v3_3, this, ms.bd.o.e2.L(v3_3, 11, "eSwwXgZ0UITZBw=="), this.LD, "eSwwXgZ0UITZBw==");
                    android.hardware.SensorManager v3_4 = this.LFFFF;
                    ms.bd.o.e2.L(v3_4, this, ms.bd.o.e2.L(v3_4, 1, "eSwwXgZ0UITZBw=="), this.LD, "eSwwXgZ0UITZBw==");
                    android.hardware.SensorManager v3_5 = this.LFFFF;
                    ms.bd.o.e2.L(v3_5, this, ms.bd.o.e2.L(v3_5, 2, "eSwwXgZ0UITZBw=="), this.LD, "eSwwXgZ0UITZBw==");
                }
            }
        } catch (String v0_18) {
            throw v0_18;
        }
        return;
    }

/**
ms.bd.o.q1;L(I J Ljava/lang/String; Ljava/lang/Object;)Ljava/lang/Object;
*/

    public final Object L(int p2, long p3, String p5, Object p6)
    {
        ms.bd.o.e2.L(ms.bd.o.a.L.LB).L();
        return 0;
    }


}