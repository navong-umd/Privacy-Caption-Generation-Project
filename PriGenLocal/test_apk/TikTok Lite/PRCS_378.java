/*Application Package Name: com.tiktok.lite.go
class PRCS_378 {
/**
X.2UE;invoke(Ljava/lang/Object;)Ljava/lang/Object;
*/

    public final synthetic Object invoke(Object p23)
    {
        android.hardware.camera2.CameraManager v11 = this.L;
        String v4 = this.LB;
        android.hardware.camera2.CameraDevice$StateCallback v3 = this.LBL;
        android.os.Handler v2 = this.LC;
        com.bytedance.helios.statichook.api.HeliosApiHook v6_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v12 = new Object[3];
        v12[0] = v4;
        v12[1] = v3;
        v12[2] = v2;
        com.bytedance.helios.statichook.api.ExtraInfo v13_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;Landroid/hardware/camera2/CameraDevice$StateCallback;Landroid/os/Handler;)V", "dzBzEgAjS8/YVFkiQFyGdpIIcIGkM9tlnBcBz8JkU7S83oC39JceYzy+GBSptlI1");
        if (!v6_1.preInvoke(100206, "android/hardware/camera2/CameraManager", "openCamera", v11, v12, "void", v13_1).intercept) {
            v11.openCamera(v4, v3, v2);
            v6_1.postInvoke(0, 100206, "android/hardware/camera2/CameraManager", "openCamera", v11, v12, v13_1, 1);
        } else {
            v6_1.postInvoke(0, 100206, "android/hardware/camera2/CameraManager", "openCamera", v11, v12, v13_1, 0);
        }
        return kotlin.Unit.L;
    }


}