package se.kth.id2223.humanactivityrecognition;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.support.v7.app.AppCompatActivity;
import android.widget.TextView;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity implements SensorEventListener, TextToSpeech.OnInitListener {

  private static final int N_SAMPLES = 100;
  private static List<Float> x;
  private static List<Float> y;
  private static List<Float> z;
  private TextView bikingTextView;

  private TextView stairuUPTextView;
  private TextView sittingTextView;
  private TextView standingTextView;
  private TextView stairDownTextView;
  private TextView walkingTextView;
  private TextToSpeech textToSpeech;
  private float[] results;
  private ActivityInference classifier;

  private String[] labels = {"Sitting", "Standing", "Stair up", "Walking", "Biking", "Stair down"};

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    x = new ArrayList<>();
    y = new ArrayList<>();
    z = new ArrayList<>();

    bikingTextView = (TextView) findViewById(R.id.biking_prob);
    sittingTextView = (TextView) findViewById(R.id.sitting_prob);
    standingTextView = (TextView) findViewById(R.id.standing_prob);
    walkingTextView = (TextView) findViewById(R.id.walking_prob);
    stairuUPTextView = (TextView) findViewById(R.id.stair_up_prob);
    stairDownTextView = (TextView) findViewById(R.id.stair_down_prob);

    classifier = new ActivityInference(getApplicationContext());

    textToSpeech = new TextToSpeech(this, this);
    textToSpeech.setLanguage(Locale.US);
  }

  @Override
  public void onInit(int status) {
    Timer timer = new Timer();
    timer.scheduleAtFixedRate(new TimerTask() {
      @Override
      public void run() {
        if (results == null || results.length == 0) {
          return;
        }
        float max = -1;
        int idx = -1;
        for (int i = 0; i < results.length; i++) {
          if (results[i] > max) {
            idx = i;
            max = results[i];
          }
        }

        textToSpeech.speak(labels[idx], TextToSpeech.QUEUE_ADD, null, Integer.toString(new Random().nextInt()));
      }
    }, 2000, 5000);
  }

  protected void onPause() {
    getSensorManager().unregisterListener(this);
    super.onPause();
  }

  protected void onResume() {
    super.onResume();
    getSensorManager().registerListener(this, getSensorManager().getDefaultSensor(Sensor.TYPE_ACCELEROMETER), SensorManager.SENSOR_DELAY_GAME);
  }

  @Override
  public void onSensorChanged(SensorEvent event) {
    activityPrediction();
    x.add(event.values[0]);
    y.add(event.values[1]);
    z.add(event.values[2]);
  }

  @Override
  public void onAccuracyChanged(Sensor sensor, int i) {

  }

  private void activityPrediction() {
    if (x.size() == N_SAMPLES && y.size() == N_SAMPLES && z.size() == N_SAMPLES) {
      List<Float> data = new ArrayList<>();
      data.addAll(x);
      data.addAll(y);
      data.addAll(z);

      results = classifier.getActivityProbabilities(toFloatArray(data));

      bikingTextView.setText(Float.toString(round(results[0], 2)));
      stairuUPTextView.setText(Float.toString(round(results[1], 2)));
      sittingTextView.setText(Float.toString(round(results[2], 2)));
      standingTextView.setText(Float.toString(round(results[3], 2)));
      stairDownTextView.setText(Float.toString(round(results[4], 2)));
      walkingTextView.setText(Float.toString(round(results[5], 2)));

      x.clear();
      y.clear();
      z.clear();
    }
  }

  private float[] toFloatArray(List<Float> list) {
    int i = 0;
    float[] array = new float[list.size()];

    for (Float f : list) {
      array[i++] = (f != null ? f : Float.NaN);
    }
    return array;
  }

  private static float round(float d, int decimalPlace) {
    BigDecimal bd = new BigDecimal(Float.toString(d));
    bd = bd.setScale(decimalPlace, BigDecimal.ROUND_HALF_UP);
    return bd.floatValue();
  }

  private SensorManager getSensorManager() {
    return (SensorManager) getSystemService(SENSOR_SERVICE);
  }

}
