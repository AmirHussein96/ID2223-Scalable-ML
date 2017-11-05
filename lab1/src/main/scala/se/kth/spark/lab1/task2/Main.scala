package se.kth.spark.lab1.task2

import org.apache.spark.sql.functions.{min, max}
import se.kth.spark.lab1._
import org.apache.spark.ml.feature.RegexTokenizer
import org.apache.spark.ml.Pipeline
import org.apache.spark.SparkConf
import org.apache.spark.SparkContext
import org.apache.spark.ml.linalg.{DenseVector, Vectors}
import org.apache.spark.sql.SQLContext

object Main {
  def main(args: Array[String]) {
    val conf = new SparkConf().setAppName("lab1").setMaster("local")
    val sc = new SparkContext(conf)
    val sqlContext = new SQLContext(sc)

    import sqlContext.implicits._
    import sqlContext._
    import org.apache.spark.sql.functions.udf

    val filePath = "src/main/resources/millionsong.txt"
    val rawDF = sc.textFile(filePath).toDF("raw").cache()

    rawDF.printSchema()

    //Step1: tokenize each row
    val regexTokenizer = new RegexTokenizer()
      .setInputCol("raw")
      .setOutputCol("parsed")
      .setPattern(",")

    //Step2: transform with tokenizer and show 5 rows
    val transformed = regexTokenizer.transform(rawDF).drop("raw")

    transformed.show(5)

    //Step3: transform array of tokens to a vector of tokens (use our ArrayToVector)
    val arr2Vect = new Array2Vector()
    arr2Vect.setInputCol("parsed")
    arr2Vect.setOutputCol("vector")
    val vectorDf = arr2Vect.transform(transformed).drop("parsed")

    vectorDf.printSchema()

    val headValue = udf((arr: DenseVector) => arr.values(0))
    //Step4: extract the label(year) into a new column
    val lSlicer = vectorDf.withColumn("label", headValue(vectorDf("vector")))

    lSlicer.show(5)
    lSlicer.printSchema()

    //Step5: convert type of the label from vector to double (use our Vector2Double)
    // It is already double?
    //val v2d = new Vector2DoubleUDF(???)
    //???

    //Step6: shift all labels by the value of minimum label such that the value of the smallest becomes 0 (use our DoubleUDF)
    val minYear = lSlicer.agg(min(lSlicer.col("label"))).map(r => r.getDouble(0)).head
    val shift = (year: Double) => year - minYear
    val lShifter = new DoubleUDF(shift)
    lShifter.setInputCol("label")
    lShifter.setOutputCol("shifted_label")
    val yearShifted = lShifter.transform(lSlicer)

    yearShifted.show(5)
    //Step7: extract just the 3 first features in a new vector column
    val fSlicer = ???

    //Step8: put everything together in a pipeline
    val pipeline = new Pipeline().setStages(???)

    //Step9: generate model by fitting the rawDf into the pipeline
    val pipelineModel = pipeline.fit(rawDF)

    //Step10: transform data with the model
    ???

    //Step11: drop all columns from the dataframe other than label and features
    ???
  }
}